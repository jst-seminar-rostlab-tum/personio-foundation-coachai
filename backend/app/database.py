from collections.abc import Generator
from typing import Any

from sqlmodel import Session, SQLModel, create_engine

from app.config import Settings

settings = Settings()

# Always use sslmode=require (TLS encryption without verifying a local CA file)
ssl_suffix = '?sslmode=require'

# Build the full database URL in one shot
DATABASE_URL = (
    f'postgresql+psycopg2://'
    f'{settings.supabase_user}:{settings.supabase_password}'
    f'@db.{settings.supabase_project_id}.supabase.co:{settings.supabase_port}'
    f'/{settings.supabase_db}{ssl_suffix}'
    if settings.supabase_environment == 'remote'
    else f'postgresql://{settings.supabase_user}:{settings.supabase_password}@127.0.0.1:5432/postgres'
)


# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)


# Create all tables
def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


# Dependency to get a DB session
def get_session() -> Generator[Session, Any, None]:
    with Session(engine) as session:
        yield session
