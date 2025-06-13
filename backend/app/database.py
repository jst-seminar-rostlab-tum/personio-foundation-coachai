import os
import urllib.request
from collections.abc import Generator
from typing import Any

from sqlmodel import Session as DBSession
from sqlmodel import SQLModel, create_engine

from app.config import Settings

settings = Settings()

if settings.stage == 'prod':
    os.makedirs(settings.ssl_cert_dir, exist_ok=True)
    ssl_cert_path = f'{settings.ssl_cert_dir}{settings.ssl_cert_name}'
    urllib.request.urlretrieve(settings.ssl_cert_url, ssl_cert_path)
else:
    ssl_cert_path = None

if settings.database_url:
    SQLALCHEMY_DATABASE_URL = (
        f'{settings.database_url}?sslmode=verify-full&sslrootcert={ssl_cert_path}'
    )
else:
    SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}'
    # SQLALCHEMY_DATABASE_URL = f'postgresql+psycopg://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}'

# Configure engine with connection pooling and prepared statement settings
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'prepared_statements': False})


# Create the database tables
def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


# Dependency to get the database session
def get_db_session() -> Generator[DBSession, Any, None]:
    with DBSession(engine) as db_session:
        try:
            yield db_session
        finally:
            db_session.close()
