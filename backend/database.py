from collections.abc import Generator
from typing import Any

from sqlmodel import Session, SQLModel, create_engine

from .config import settings

# Database connection string
SQLALCHEMY_DATABASE_URL = f'postgresql+psycopg://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}'
engine = create_engine(SQLALCHEMY_DATABASE_URL)


# Create the database tables
def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


# Dependency to get the database session
def get_session() -> Generator[Session, Any, None]:
    with Session(engine) as session:
        yield session
