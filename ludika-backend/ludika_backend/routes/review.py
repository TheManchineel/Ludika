from fastapi import APIRouter, HTTPException, Depends
from fastapi.params import Security
from sqlmodel import Session, delete, select, or_
from typing import List
from datetime import datetime
from uuid import UUID

from ludika_backend.controllers.auth import get_current_user, get_current_user_optional
from ludika_backend.models.review import (
    ReviewCriterion,
    ReviewCriterionCreate,
    ReviewCriterionUpdate,
    CriterionWeightProfile,
    CriterionWeightProfileCreate,
    CriterionWeightProfileUpdate,
    CriterionWeight,
    CriterionWeightCreate,
    Review,
    ReviewUpdate,
    ReviewCreate,
    ReviewRating,
    ReviewRatingCreate,
    CriterionWeightProfilePublic,
    ReviewPublic,
)
from ludika_backend.models.users import User, UserRole
from ludika_backend.models.games import Game, GameStatus
from ludika_backend.utils.db import get_session

review_router = APIRouter()


def _handle_profile_weights(
    db_session: Session,
    profile_id: int,
    weights: List[CriterionWeightCreate],
    current_user: User,
):
    """
    Helper function to handle bulk weight operations for a profile.
    This function replaces all existing weights with the new ones.
    """
    db_profile = db_session.get(CriterionWeightProfile, profile_id)
    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    if (
        db_profile.is_global
        and current_user.user_role != UserRole.PLATFORM_ADMINISTRATOR
    ):
        raise HTTPException(
            status_code=403, detail="Only admins can modify global profiles."
        )
    if not db_profile.is_global and db_profile.user_id != current_user.uuid:
        raise HTTPException(status_code=403, detail="You do not own this profile.")

    db_session.exec(
        delete(CriterionWeight).where(CriterionWeight.profile_id == profile_id)
    )

    for weight_data in weights:
        db_weight = CriterionWeight.model_validate(
            weight_data, update={"profile_id": profile_id}
        )
        db_session.add(db_weight)

    db_session.commit()


def _check_game_access_and_approved(
    db_session: Session,
    game_id: int,
    current_user: User | None = None,
    require_approved: bool = True,
) -> Game:
    """
    Helper function to check if a game exists, is accessible, and optionally is approved.
    """
    game_statement = select(Game).where(Game.id == game_id)
    
    if current_user:
        if not current_user.is_privileged():
            game_statement = game_statement.where(
                or_(
                    Game.proposing_user == current_user.uuid,
                    Game.status == GameStatus.APPROVED.value,
                )
            )
    else:
        game_statement = game_statement.where(Game.status == GameStatus.APPROVED.value)

    game = db_session.exec(game_statement).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    if require_approved and game.status != GameStatus.APPROVED:
        raise HTTPException(
            status_code=400, 
            detail="Reviews can only be created for approved games."
        )
    
    return game


# --- ReviewCriterion Endpoints ---
@review_router.get("/criteria")
async def list_criteria(
    db_session: Session = Depends(get_session),
) -> List[ReviewCriterion]:
    """Get all review criteria."""
    return db_session.exec(select(ReviewCriterion)).all()


@review_router.post("/criteria")
async def create_criterion(
    criterion: ReviewCriterionCreate,
    db_session: Session = Depends(get_session),
    current_user: User = Security(get_current_user),
) -> ReviewCriterion:
    """Create a new review criterion (admin only)."""
    if current_user.user_role != UserRole.PLATFORM_ADMINISTRATOR:
        raise HTTPException(status_code=403, detail="Only admins can create criteria.")
    db_criterion = ReviewCriterion.model_validate(criterion)
    db_session.add(db_criterion)
    db_session.commit()
    db_session.refresh(db_criterion)
    return db_criterion


@review_router.patch("/criteria/{criterion_id}")
async def update_criterion(
    criterion_id: int,
    update: ReviewCriterionUpdate,
    db_session: Session = Depends(get_session),
    current_user: User = Security(get_current_user),
) -> ReviewCriterion:
    """Update a review criterion (admin only)."""
    if current_user.user_role != UserRole.PLATFORM_ADMINISTRATOR:
        raise HTTPException(status_code=403, detail="Only admins can update criteria.")
    db_criterion = db_session.get(ReviewCriterion, criterion_id)
    if not db_criterion:
        raise HTTPException(status_code=404, detail="Criterion not found")
    db_criterion.sqlmodel_update(update.model_dump(exclude_unset=True))
    db_session.commit()
    db_session.refresh(db_criterion)
    return db_criterion


@review_router.delete("/criteria/{criterion_id}")
async def delete_criterion(
    criterion_id: int,
    db_session: Session = Depends(get_session),
    current_user: User = Security(get_current_user),
):
    """Delete a review criterion (admin only)."""
    if current_user.user_role != UserRole.PLATFORM_ADMINISTRATOR:
        raise HTTPException(status_code=403, detail="Only admins can delete criteria.")
    db_criterion = db_session.get(ReviewCriterion, criterion_id)
    if not db_criterion:
        raise HTTPException(status_code=404, detail="Criterion not found")
    db_session.delete(db_criterion)
    db_session.commit()
    return {"status": "ok"}


# --- CriterionWeightProfile Endpoints ---
@review_router.get("/profiles")
async def list_profiles(
    db_session: Session = Depends(get_session),
    current_user: User | None = Security(get_current_user_optional),
) -> List[CriterionWeightProfilePublic]:
    """Get available criterion weight profiles."""
    if current_user is None:
        condition = CriterionWeightProfile.is_global == True
    else:
        condition = or_(
            CriterionWeightProfile.is_global == True,
            CriterionWeightProfile.user_id == current_user.uuid,
        )

    return db_session.exec(select(CriterionWeightProfile).where(condition)).all()


@review_router.post("/profiles")
async def create_profile(
    profile: CriterionWeightProfileCreate,
    db_session: Session = Depends(get_session),
    current_user: User = Security(get_current_user),
) -> CriterionWeightProfilePublic:
    """Create a new criterion weight profile."""
    if profile.is_global and current_user.user_role != UserRole.PLATFORM_ADMINISTRATOR:
        raise HTTPException(
            status_code=403, detail="Only admins can create global profiles."
        )

    weights = profile.weights
    profile_data = profile.model_dump(exclude={"weights"})

    db_profile = CriterionWeightProfile.model_validate(
        profile_data, update={"user_id": current_user.uuid}
    )

    db_session.add(db_profile)
    db_session.commit()  # Commit first to get the profile ID
    db_session.refresh(db_profile)

    if weights:
        _handle_profile_weights(db_session, db_profile.id, weights, current_user)

    # get the profile with the weights
    db_session.refresh(db_profile)
    return db_profile


@review_router.patch("/profiles/{profile_id}")
async def update_profile(
    profile_id: int,
    update: CriterionWeightProfileUpdate,
    db_session: Session = Depends(get_session),
    current_user: User = Security(get_current_user),
) -> CriterionWeightProfilePublic:
    """Update a criterion weight profile."""
    db_profile = db_session.get(CriterionWeightProfile, profile_id)
    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    if (
        db_profile.is_global
        and current_user.user_role != UserRole.PLATFORM_ADMINISTRATOR
    ):
        raise HTTPException(
            status_code=403, detail="Only admins can update global profiles."
        )
    if not db_profile.is_global and db_profile.user_id != current_user.uuid:
        raise HTTPException(status_code=403, detail="You do not own this profile.")

    update_data = update.model_dump(exclude_unset=True)
    weights = update_data.pop("weights", None)

    db_profile.sqlmodel_update(update_data)
    if weights is not None:
        _handle_profile_weights(db_session, db_profile.id, weights, current_user)

    db_session.commit()
    db_session.refresh(db_profile)
    return db_profile


@review_router.delete("/profiles/{profile_id}")
async def delete_profile(
    profile_id: int,
    db_session: Session = Depends(get_session),
    current_user: User = Security(get_current_user),
):
    """Delete a criterion weight profile."""
    db_profile = db_session.get(CriterionWeightProfile, profile_id)
    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    if (
        db_profile.is_global
        and current_user.user_role != UserRole.PLATFORM_ADMINISTRATOR
    ):
        raise HTTPException(
            status_code=403, detail="Only admins can delete global profiles."
        )
    if not db_profile.is_global and db_profile.user_id != current_user.uuid:
        raise HTTPException(status_code=403, detail="You do not own this profile.")
    db_session.delete(db_profile)
    db_session.commit()
    return {"status": "ok"}


# --- Review Endpoints ---
@review_router.get("/{game_id}")
async def get_game_reviews(
    game_id: int,
    db_session: Session = Depends(get_session),
    current_user: User | None = Security(get_current_user_optional),
) -> List[ReviewPublic]:
    """
    Get all reviews for a specific game.
    """
    _check_game_access_and_approved(db_session, game_id, current_user, require_approved=False)
    
    reviews = db_session.exec(
        select(Review).where(Review.game_id == game_id)
    ).all()
    
    return reviews


@review_router.get("/{game_id}/my-review")
async def get_my_review(
    game_id: int,
    db_session: Session = Depends(get_session),
    current_user: User = Security(get_current_user),
) -> ReviewPublic:
    """
    Get the current user's review for a specific game, if it exists.
    """
    _check_game_access_and_approved(db_session, game_id, current_user, require_approved=False)
    
    review = db_session.exec(
        select(Review).where(
            Review.game_id == game_id,
            Review.reviewer_id == current_user.uuid
        )
    ).first()
    
    if not review:
        raise HTTPException(status_code=404, detail="You have not reviewed this game yet.")
    
    return review


@review_router.put("/{game_id}/my-review")
async def create_or_update_my_review(
    game_id: int,
    review: ReviewCreate,
    db_session: Session = Depends(get_session),
    current_user: User = Security(get_current_user),
) -> ReviewPublic:
    """
    Create a new review or replace existing review for the current user.
    Only allowed for approved games.
    """
    _check_game_access_and_approved(db_session, game_id, current_user, require_approved=True)
    
    # Check if review already exists
    existing_review = db_session.exec(
        select(Review).where(
            Review.game_id == game_id,
            Review.reviewer_id == current_user.uuid
        )
    ).first()
    
    if existing_review:
        # Update existing review
        update_data = review.model_dump(exclude={"ratings"})
        existing_review.sqlmodel_update(update_data)
        existing_review.updated_at = datetime.utcnow()
        
        # Delete existing ratings
        db_session.exec(
            delete(ReviewRating).where(
                ReviewRating.game_id == game_id,
                ReviewRating.reviewer_id == current_user.uuid
            )
        )
        
        # Add new ratings
        if review.ratings:
            for rating_data in review.ratings:
                db_rating = ReviewRating.model_validate(
                    rating_data, 
                    update={
                        "game_id": game_id,
                        "reviewer_id": current_user.uuid
                    }
                )
                db_session.add(db_rating)
        
        db_session.commit()
        db_session.refresh(existing_review)
        return existing_review
    else:
        # Create new review
        review_data = review.model_dump(exclude={"ratings"})
        db_review = Review.model_validate(
            review_data,
            update={
                "game_id": game_id,
                "reviewer_id": current_user.uuid,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            },
        )
        db_session.add(db_review)
        db_session.commit()
        db_session.refresh(db_review)
        
        # Add ratings if provided
        if review.ratings:
            for rating_data in review.ratings:
                db_rating = ReviewRating.model_validate(
                    rating_data,
                    update={
                        "game_id": game_id,
                        "reviewer_id": current_user.uuid
                    }
                )
                db_session.add(db_rating)
            db_session.commit()
            db_session.refresh(db_review)
        
        return db_review


@review_router.delete("/{game_id}/my-review")
async def delete_my_review(
    game_id: int,
    db_session: Session = Depends(get_session),
    current_user: User = Security(get_current_user),
):
    """
    Delete the current user's review for a specific game, if it exists.
    """
    _check_game_access_and_approved(db_session, game_id, current_user, require_approved=False)
    
    review = db_session.exec(
        select(Review).where(
            Review.game_id == game_id,
            Review.reviewer_id == current_user.uuid
        )
    ).first()
    
    if not review:
        raise HTTPException(status_code=404, detail="You have not reviewed this game yet.")
    
    db_session.delete(review)
    db_session.commit()
    return {"status": "ok"}


@review_router.get("/{game_id}/{user_id}")
async def get_user_review(
    game_id: int,
    user_id: UUID,
    db_session: Session = Depends(get_session),
    current_user: User | None = Security(get_current_user_optional),
) -> ReviewPublic:
    """
    Get a specific user's review for a specific game, if it exists.
    """
    _check_game_access_and_approved(db_session, game_id, current_user, require_approved=False)
    
    review = db_session.exec(
        select(Review).where(
            Review.game_id == game_id,
            Review.reviewer_id == user_id
        )
    ).first()
    
    if not review:
        raise HTTPException(status_code=404, detail="Review not found.")
    
    return review


@review_router.delete("/{game_id}/{user_id}")
async def delete_user_review(
    game_id: int,
    user_id: UUID,
    db_session: Session = Depends(get_session),
    current_user: User = Security(get_current_user),
):
    """
    Delete a specific user's review for a specific game. Only privileged users can do this.
    """
    if not current_user.is_privileged():
        raise HTTPException(
            status_code=403, 
            detail="Only privileged users can delete other users' reviews."
        )
    
    _check_game_access_and_approved(db_session, game_id, current_user, require_approved=False)
    
    review = db_session.exec(
        select(Review).where(
            Review.game_id == game_id,
            Review.reviewer_id == user_id
        )
    ).first()
    
    if not review:
        raise HTTPException(status_code=404, detail="Review not found.")
    
    db_session.delete(review)
    db_session.commit()
    return {"status": "ok"}
