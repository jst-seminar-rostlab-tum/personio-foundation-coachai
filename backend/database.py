from collections.abc import Generator
from typing import Any

from sqlmodel import Session, SQLModel, create_engine
import os
from dotenv import load_dotenv
# from .config import settings

# Load environment variables from .env file
load_dotenv()

# Database connection parameters from .env
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DB = os.getenv("POSTGRES_DB")

# Database connection string
SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)
print(SQLALCHEMY_DATABASE_URL)
engine = create_engine(SQLALCHEMY_DATABASE_URL)


# Create the database tables
def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


# Dependency to get the database session
def get_session() -> Generator[Session, Any, None]:
    with Session(engine) as session:
        yield session

