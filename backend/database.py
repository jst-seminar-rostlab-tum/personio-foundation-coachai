from collections.abc import Generator
from typing import Any

from sqlmodel import Session, SQLModel, create_engine

from .config import settings

SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}'

engine = create_engine(SQLALCHEMY_DATABASE_URL)


def create_db_and_tables() -> None:
    """
    Create the database and tables if they do not exist.
    """
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, Any, None]:
    """
    Get a database session.
    """
    with Session(engine) as session:
        yield session
