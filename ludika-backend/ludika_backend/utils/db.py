from enum import Enum

from sqlmodel import create_engine, Session, Column, Field
from sqlalchemy.dialects.postgresql import ENUM as SqlEnum
from sqlalchemy.engine import Engine

from ..utils.config import get_config_value

engine: Engine | None = None


def make_connection_string() -> str:
    return (
        "postgresql+psycopg://"
        f"{get_config_value('Database', 'user')}"
        ":"
        f"{get_config_value('Database', 'password')}"
        "@"
        f"{get_config_value('Database', 'host')}"
        ":"
        f"{get_config_value('Database', 'port')}"
        "/"
        f"{get_config_value('Database', 'dbname')}"
    )


def get_engine() -> Engine:
    """
    Returns a SQLAlchemy engine for the database.
    """

    global engine
    if engine:
        return engine

    engine = create_engine(make_connection_string(), echo=True)
    return engine


def get_session():
    """
    Returns a SQLAlchemy session for the database.
    """
    with Session(get_engine()) as session:
        yield session


def make_enum_field(enum_class: type[Enum], nullable: bool = False, default=None):
    return Field(
        sa_column=Column(
            SqlEnum(
                enum_class,
                values_callable=lambda enum: [member.value for member in enum],
            ),
            nullable=nullable,
            default=default,
        )
    )
