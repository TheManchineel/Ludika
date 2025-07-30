from datetime import datetime
from enum import Enum

from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID
from typing import TYPE_CHECKING

from ludika_backend.utils.db import make_enum_field

if TYPE_CHECKING:
    from ludika_backend.models.review import Review, ReviewPublic


class GameStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"


class GameTag(SQLModel, table=True):
    """
    Game-Tag association table
    """

    id: int
    game_id: int = Field(foreign_key="game.id", primary_key=True)
    tag_id: int = Field(foreign_key="tag.id", primary_key=True)


class GameBase(SQLModel):
    """
    Represents a game in the system.
    """

    class Config:
        """Make the JSON array in the `images` field compatible with SQLAlchemy"""

        arbitrary_types_allowed = True

    name: str
    description: str | None
    url: str


class Game(GameBase, table=True):
    id: int | None = Field(primary_key=True, default=None)
    tags: list["Tag"] = Relationship(back_populates="games", link_model=GameTag)

    proposing_user: UUID | None
    status: GameStatus = make_enum_field(GameStatus)
    approved_by: UUID | None = Field(default=None)
    created_at: datetime = Field(default=None)
    updated_at: datetime = Field(default=None)
    images: list["GameImage"] = Relationship(back_populates="game")
    reviews: list["Review"] = Relationship(back_populates="game")

    def is_visible_by(self, user) -> bool:
        if user is None:
            return self.status == GameStatus.APPROVED
        if user.is_privileged():
            return True
        return self.proposing_user == user.uuid or self.status == GameStatus.APPROVED


class GameImage(SQLModel, table=True):
    game_id: int = Field(foreign_key="game.id", primary_key=True)
    position: int = Field(primary_key=True)
    image: str
    game: Game = Relationship(back_populates="images")


class GameImagePublic(SQLModel):
    position: int
    image: str


class GamePublic(GameBase):
    """
    Represents a game with public fields.
    """

    id: int
    created_at: datetime
    updated_at: datetime
    tags: list["Tag"] = []
    images: list[GameImagePublic] | None = []
    status: GameStatus
    proposing_user: UUID | None


class GameWithReviews(GamePublic):
    """
    Represents a game with public fields and reviews.
    """

    reviews: list["ReviewPublic"] = []


class GameCreate(GameBase):
    """
    Represents a game creation request.
    """

    tags: list[int] | None = None


class GameUpdate(SQLModel):
    """
    Represents a game update request.
    """

    name: str | None = None
    description: str | None = None
    url: str | None = None
    tags: list[int] | None = None
    status: GameStatus | None = None


class TagBase(SQLModel):
    name: str
    icon: str | None


class Tag(TagBase, table=True):
    """
    Represents a game tag
    """

    id: int = Field(primary_key=True)
    games: list["Game"] = Relationship(back_populates="tags", link_model=GameTag)


class TagCreate(TagBase):
    pass


class TagUpdate(SQLModel):
    name: str | None = None
    icon: str | None = None
