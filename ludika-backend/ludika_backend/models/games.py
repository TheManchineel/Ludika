from datetime import datetime
from sqlmodel import Column, SQLModel, Field, String, Relationship
from sqlalchemy.dialects.postgresql import ARRAY
from uuid import UUID


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
        """Make the JSON array in images field compatible with SQLAlchemy"""

        arbitrary_types_allowed = True

    name: str
    description: str | None
    url: str
    icon: str | None


class Game(GameBase, table=True):
    id: int | None = Field(primary_key=True, default=None)
    tags: list["Tag"] = Relationship(back_populates="games", link_model=GameTag)

    proposing_user: UUID | None
    approved: bool | None = Field(default=None)
    approved_by: UUID | None = Field(default=None)
    created_at: datetime = Field(default=None)
    updated_at: datetime = Field(default=None)
    images: list[str] | None = Field(sa_column=Column(ARRAY(String)), default=None)


class GamePublic(GameBase):
    """
    Represents a game with public fields.
    """

    id: int
    created_at: datetime
    updated_at: datetime
    tags: list["Tag"] = []
    images: list[str] | None


class GameCreate(GameBase):
    """
    Represents a game creation request.
    """

    tags: list[int] | None = None


class GameUpdate(GameBase):
    """
    Represents a game update request.
    """

    name: str | None = None
    description: str | None = None
    url: str | None = None
    icon: str | None = None
    tags: list[int] | None = None


class Tag(SQLModel, table=True):
    """
    Represents a game tag
    """

    id: int = Field(primary_key=True)
    name: str
    games: list["Game"] = Relationship(back_populates="tags", link_model=GameTag)
