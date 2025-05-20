from collections.abc import Generator
from typing import Any
from sqlmodel import SQLModel, create_engine, Session


# from .config import settings

# SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}'

# SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}?sslmode=require"
# Database connection parameters


# POSTGRES_USER = 'postgres'
# POSTGRES_PASSWORD = 'zusjyx-Hedkyr-wevwi9'  
# POSTGRES_HOST = 'db.qgqfapwoopmzrkartwfw.supabase.co'
# POSTGRES_PORT = '5432'
# POSTGRES_DB = 'postgres'


# Database connection string
#  Depend on your network the first option is Direct connection and the second one is transaction pool
# SQLALCHEMY_DATABASE_URL = (
#     'postgresql://postgres:zusjyx-Hedkyr-wevwi9@db.qgqfapwoopmzrkartwfw.supabase.co:5432/postgres'
# )
SQLALCHEMY_DATABASE_URL = "postgresql://postgres.syucjzgfvvmwsnairifl:fawgUs-9vujto-wyxgit@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"

engine = create_engine(SQLALCHEMY_DATABASE_URL)


# Create the database tables
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


# Dependency to get the database session
def get_session() -> Generator[Session, Any, None]:
    with Session(engine) as session:
        yield session

