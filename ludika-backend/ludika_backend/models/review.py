from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ludika_backend.models.users import UserPublic, User
    from ludika_backend.models.games import Game


# --- Review Criterion ---
class ReviewCriterionBase(SQLModel):
    name: str
    description: Optional[str] = None


class ReviewCriterion(ReviewCriterionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    ratings: List["ReviewRating"] = Relationship(
        back_populates="criterion", cascade_delete=True
    )
    weights: List["CriterionWeight"] = Relationship(
        back_populates="criterion", cascade_delete=True
    )


class ReviewCriterionCreate(ReviewCriterionBase):
    pass


class ReviewCriterionUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None


class CriterionWeightProfileBase(SQLModel):
    name: str
    is_global: bool = False


class CriterionWeightProfile(CriterionWeightProfileBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[UUID] = Field(foreign_key="users.uuid")
    weights: List["CriterionWeight"] = Relationship(
        back_populates="profile", cascade_delete=True
    )


class CriterionWeightProfilePublic(CriterionWeightProfileBase):
    id: int
    user_id: UUID
    is_global: bool
    weights: List["CriterionWeightPublic"] = []


class CriterionWeightProfileCreate(CriterionWeightProfileBase):
    weights: Optional[List["CriterionWeightCreate"]] = None


class CriterionWeightProfileUpdate(SQLModel):
    name: Optional[str] = None
    is_global: Optional[bool] = None
    weights: Optional[List["CriterionWeightCreate"]] = None


# --- Criterion Weight ---
class CriterionWeightBase(SQLModel):
    weight: float


class CriterionWeight(CriterionWeightBase, table=True):
    profile_id: int = Field(
        foreign_key="criterionweightprofile.id", primary_key=True, ondelete="CASCADE"
    )
    criterion_id: int = Field(
        foreign_key="reviewcriterion.id", primary_key=True, ondelete="CASCADE"
    )
    profile: "CriterionWeightProfile" = Relationship(back_populates="weights")
    criterion: "ReviewCriterion" = Relationship(back_populates="weights")


class CriterionWeightPublic(CriterionWeightBase):
    criterion_id: int


class CriterionWeightCreate(CriterionWeightBase):
    criterion_id: int


class CriterionWeightUpdate(SQLModel):
    weight: Optional[float] = None


# --- Review Rating Models ---
class ReviewRatingBase(SQLModel):
    score: int


class ReviewRating(ReviewRatingBase, table=True):
    game_id: int = Field(foreign_key="game.id", primary_key=True, ondelete="CASCADE")
    reviewer_id: UUID = Field(
        foreign_key="users.uuid", primary_key=True, ondelete="CASCADE"
    )
    criterion_id: int = Field(
        foreign_key="reviewcriterion.id", primary_key=True, ondelete="CASCADE"
    )
    score: int = Field(..., ge=1, le=5)
    review: "Review" = Relationship(
        back_populates="ratings",
        sa_relationship_kwargs={
            "primaryjoin": "and_(foreign(ReviewRating.game_id) == Review.game_id, foreign(ReviewRating.reviewer_id) == Review.reviewer_id)"
        },
    )
    criterion: "ReviewCriterion" = Relationship(back_populates="ratings")


class ReviewRatingCreate(ReviewRatingBase):
    criterion_id: int


class ReviewRatingUpdate(SQLModel):
    score: Optional[int] = None


class ReviewRatingPublic(ReviewRatingBase):
    criterion: "ReviewCriterion" = {}


# --- Review Models ---
class ReviewBase(SQLModel):
    review_text: Optional[str] = None


class Review(ReviewBase, table=True):
    game_id: int = Field(primary_key=True, foreign_key="game.id", ondelete="CASCADE")
    reviewer_id: UUID = Field(
        primary_key=True, foreign_key="users.uuid", ondelete="CASCADE"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    ratings: list["ReviewRating"] = Relationship(
        back_populates="review",
        sa_relationship_kwargs={
            "primaryjoin": "and_(Review.game_id == foreign(ReviewRating.game_id), Review.reviewer_id == foreign(ReviewRating.reviewer_id))"
        },
        cascade_delete=True,
    )
    author: "User" = Relationship(back_populates="reviews")
    game: "Game" = Relationship(back_populates="reviews")


class ReviewPublic(ReviewBase):
    game_id: int
    reviewer_id: UUID
    author: "UserPublic" = {}
    created_at: datetime
    updated_at: datetime
    ratings: List[ReviewRatingPublic] = []


class ReviewCreate(ReviewBase):
    ratings: Optional[List[ReviewRatingCreate]] = None


class ReviewUpdate(SQLModel):
    review_text: Optional[str] = None
    ratings: Optional[List[ReviewRatingCreate]] = None
