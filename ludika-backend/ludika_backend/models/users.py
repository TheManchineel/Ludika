from datetime import datetime
from pydantic import SecretStr
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum
from uuid import UUID
from typing import TYPE_CHECKING

from ludika_backend.utils.db import make_enum_field

if TYPE_CHECKING:
    from ludika_backend.models.games import Game, GameStatus


class UserRole(str, Enum):
    """
    Role of a user in the system.
    """

    USER = "user"
    CONTENT_MODERATOR = "content_moderator"
    PLATFORM_ADMINISTRATOR = "platform_administrator"

    def is_privileged(self):
        return self in [UserRole.CONTENT_MODERATOR, UserRole.PLATFORM_ADMINISTRATOR]


class UserBase(SQLModel):
    """
    Base class for user models.
    """

    visible_name: str
    user_role: UserRole = make_enum_field(UserRole)
    enabled: bool


class User(UserBase, table=True):
    """
    Represents a user in the database (all fields included).
    """

    __tablename__ = "users"  # type: ignore[assignment]

    uuid: UUID = Field(primary_key=True)
    email: str
    created_at: datetime
    last_login: datetime | None
    enabled: bool
    password_hash: str | None
    reviews: list["Review"] = Relationship(back_populates="author")

    def can_edit_game(self, game: "Game"):
        if self.user_role.is_privileged():
            return True
        if game.proposing_user == self.uuid and game.status == "draft":
            return True
        return False

    def can_access_game(self, game: "Game"):
        if self.user_role.is_privileged():
            return True
        if game.status == "approved":
            return True
        if game.proposing_user == self.uuid:
            return True
        return False

    def is_privileged(self):
        return self.user_role.is_privileged()


class UserPublic(UserBase):
    """
    Represents a public view of a user.
    """

    uuid: UUID
    created_at: datetime
    last_login: datetime | None


class UserUpdateVisibleName(SQLModel):
    visible_name: str


class UserUpdatePassword(SQLModel):
    password: SecretStr


class UserAdminUpdate(SQLModel):
    enabled: bool | None = None
    user_role: UserRole | None = None
