import os
import urllib.request
from collections.abc import Generator
from typing import Any

from sqlmodel import Session as DBSession
from sqlmodel import create_engine
from supabase import Client, create_client

from app.config import Settings

settings = Settings()

if settings.stage == 'prod':
    os.makedirs(settings.ssl_cert_dir, exist_ok=True)
    ssl_cert_path = f'{settings.ssl_cert_dir}{settings.ssl_cert_name}'
    urllib.request.urlretrieve(settings.ssl_cert_url, ssl_cert_path)
else:
    ssl_cert_path = None


if settings.database_url:
    if settings.stage == 'prod' and ssl_cert_path:
        SQLALCHEMY_DATABASE_URL = f'{settings.database_url}?sslrootcert={ssl_cert_path}'
    else:
        SQLALCHEMY_DATABASE_URL = settings.database_url
else:
    SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:postgres@127.0.0.1:54322/postgres'
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_size=5, max_overflow=4, pool_pre_ping=True)


def get_db_session() -> Generator[DBSession, Any, None]:
    with DBSession(engine) as db_session:
        try:
            yield db_session
        finally:
            db_session.close()


def get_supabase_client() -> Client:
    if settings.SUPABASE_URL and settings.SUPABASE_SERVICE_ROLE_KEY:
        client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
        client.rpc('grant_hr_info_permissions')
        return client
    raise RuntimeError('Supabase client configuration is missing in environment variables.')
