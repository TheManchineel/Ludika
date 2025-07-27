from fastapi import APIRouter, HTTPException, Depends
from fastapi.params import Security
from sqlmodel import Session, delete, select, or_
from typing import List
from datetime import datetime

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
    ReviewRating,
    CriterionWeightProfilePublic,
    ReviewPublic,
)
from ludika_backend.models.users import User, UserRole
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


# --- ReviewCriterion Endpoints ---
@review_router.get("/criteria")
async def list_criteria(
    db_session: Session = Depends(get_session),
) -> List[ReviewCriterion]:
    return db_session.exec(select(ReviewCriterion)).all()


@review_router.post("/criteria")
async def create_criterion(
    criterion: ReviewCriterionCreate,
    db_session: Session = Depends(get_session),
    current_user: User = Security(get_current_user),
) -> ReviewCriterion:
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
    if profile.is_global and current_user.user_role != UserRole.PLATFORM_ADMINISTRATOR:
        raise HTTPException(
            status_code=403, detail="Only admins can create global profiles."
        )

    weights = profile.weights
    profile_data = profile.model_dump(exclude={"weights"})

    db_profile = CriterionWeightProfile.model_validate(
        profile_data, update={"user_id": current_user.uuid}
    )

    if weights:
        _handle_profile_weights(db_session, db_profile.id, weights, current_user)

    db_session.add(db_profile)
    db_session.commit()
    db_session.refresh(db_profile)
    return db_profile


@review_router.patch("/profiles/{profile_id}")
async def update_profile(
    profile_id: int,
    update: CriterionWeightProfileUpdate,
    db_session: Session = Depends(get_session),
    current_user: User = Security(get_current_user),
) -> CriterionWeightProfilePublic:
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


@review_router.get("/{review_id}")
async def get_review(
    review_id: int,
    db_session: Session = Depends(get_session),
    current_user: User | None = Security(get_current_user_optional),
) -> ReviewPublic:
    """
    Retrieve a specific review by its ID.
    """
    db_review = db_session.get(Review, review_id)
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")

    # Check if user can view this review (either it's their own or they're privileged)
    if current_user and not current_user.is_privileged():
        if db_review.reviewer_id != current_user.uuid:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to view this review.",
            )

    return db_review


@review_router.patch("/{review_id}")
async def update_review(
    review_id: int,
    update: ReviewUpdate,
    db_session: Session = Depends(get_session),
    current_user: User = Security(get_current_user),
) -> ReviewPublic:
    """
    Update a specific review by its ID.
    """
    db_review = db_session.get(Review, review_id)
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")

    if db_review.reviewer_id != current_user.uuid and not current_user.is_privileged():
        raise HTTPException(
            status_code=403, detail="You do not have permission to update this review."
        )

    # Update review data
    update_data = update.model_dump(exclude_unset=True, exclude={"ratings"})
    if update_data:
        db_review.sqlmodel_update(update_data)
        db_review.updated_at = datetime.utcnow()

    # Handle ratings update if provided (similar to criterion weights logic)
    if update.ratings is not None:
        # Delete existing ratings
        db_session.exec(delete(ReviewRating).where(ReviewRating.review_id == review_id))

        # Add new ratings
        for rating_data in update.ratings:
            db_rating = ReviewRating.model_validate(
                rating_data, update={"review_id": review_id}
            )
            db_session.add(db_rating)

    db_session.commit()
    db_session.refresh(db_review)
    return db_review


@review_router.delete("/{review_id}")
async def delete_review(
    review_id: int,
    db_session: Session = Depends(get_session),
    current_user: User = Security(get_current_user),
):
    """
    Delete a specific review by its ID.
    """
    db_review = db_session.get(Review, review_id)
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")

    if db_review.reviewer_id != current_user.uuid and not current_user.is_privileged():
        raise HTTPException(
            status_code=403, detail="You do not have permission to delete this review."
        )

    db_session.delete(db_review)
    db_session.commit()
    return {"status": "ok"}
