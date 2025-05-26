import os
import urllib.request
from collections.abc import Generator
from typing import Any

from sqlmodel import Session, SQLModel, create_engine

from .config import settings

if settings.stage == 'prod':
    os.makedirs(settings.ssl_cert_dir, exist_ok=True)
    ssl_cert_path = f'{settings.ssl_cert_dir}{settings.ssl_cert_name}'
    urllib.request.urlretrieve(settings.ssl_cert_url, ssl_cert_path)
else:
    ssl_cert_path = None

if settings.database_url:
    SQLALCHEMY_DATABASE_URL = f'{settings.database_url}?sslmode=verify-full&sslrootcert={ssl_cert_path}'
else:
    SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}'


# print(SQLALCHEMY_DATABASE_URL)
engine = create_engine(SQLALCHEMY_DATABASE_URL)


# Create the database tables
def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


# Dependency to get the database session
def get_session() -> Generator[Session, Any, None]:
    with Session(engine) as session:
        yield session
