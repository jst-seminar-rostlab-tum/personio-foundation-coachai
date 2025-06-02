import os
from collections.abc import Generator
from typing import Any

from sqlmodel import Session, SQLModel, create_engine

from .config import Settings

settings = Settings()

# Try to connect with SSL certificate to protect against Man-In-The-Middle attacks
cert_path = settings.supabase_ssl_cert_path
if os.path.exists(cert_path):
    print(f'Connecting with SSL certificate (verify-full) at {cert_path}')
    ssl_suffix = f'?sslmode=verify-full&sslrootcert={cert_path}'
else:
    print(
        'SSL cert not found at '
        f'{cert_path!r}; connecting with sslmode=require (TLS but no verification).'
    )
    ssl_suffix = '?sslmode=require'

# Build the full database URL in one shot
SQLALCHEMY_DATABASE_URL = (
    f'postgresql+psycopg2://'
    f'{settings.supabase_user}:{settings.supabase_password}'
    f'@{settings.supabase_host}:{settings.supabase_port}'
    f'/{settings.supabase_db}{ssl_suffix}'
)


# Create the SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)


# Create all tables
def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


# Dependency to get a DB session
def get_session() -> Generator[Session, Any, None]:
    with Session(engine) as session:
        yield session
