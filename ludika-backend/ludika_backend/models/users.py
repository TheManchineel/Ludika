from datetime import datetime
from pydantic import SecretStr
from sqlmodel import SQLModel, Field
from enum import Enum
from uuid import UUID

from ludika_backend.util.db import make_enum_field


class UserRole(str, Enum):
    """
    Role of a user in the system.
    """

    USER = "user"
    CONTENT_MODERATOR = "content_moderator"
    PLATFORM_ADMINISTRATOR = "platform_administrator"


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


class UserCreate(UserBase):
    """
    Represents a user creation request.
    """

    enabled: bool = True
    email: str
    user_role: UserRole = make_enum_field(
        UserRole, nullable=True, default=UserRole.USER
    )
    password: SecretStr


class UserUpdate(UserBase):
    """
    Represents a user update request.
    """

    uuid: UUID
    visible_name: str | None
    email: str | None
    user_role: UserRole | None = make_enum_field(UserRole, nullable=True)
    enabled: bool | None
    password: SecretStr | None


class UserSelfUpdate(UserBase):
    """
    Represents a user self-update request.
    """

    visible_name: str | None
    email: str | None
    password: SecretStr | None


class UserPublic(UserBase):
    """
    Represents a public view of a user.
    """

    uuid: UUID
    created_at: datetime
    last_login: datetime | None
