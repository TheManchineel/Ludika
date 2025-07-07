from sqlmodel import create_engine, Session
from sqlalchemy.engine import Engine

from ..util.config import get_config_value

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
