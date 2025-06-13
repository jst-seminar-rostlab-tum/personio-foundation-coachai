import logging
from collections.abc import Generator
from typing import Any
from urllib.parse import quote_plus

from sqlmodel import Session as DBSession
from sqlmodel import SQLModel, create_engine

from app.config import Settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = Settings()

# Determine database URL and log appropriately
if settings.stage == 'prod':
    logger.info('Connecting to remote Supabase.')
    print('_____________________prod')
    if not settings.SUPABASE_DB_URL:
        logger.error('SUPABASE_DB_URL required in prod!')
    SQLALCHEMY_DATABASE_URL = settings.SUPABASE_DB_URL
    logger.debug('Connected to remote Supabase.')

else:
    print('_____________________dev')

    user = 'postgres'
    password = quote_plus(settings.SUPABASE_PASSWORD)
    host = settings.SUPABASE_HOST  # Should be "db" in docker-compose
    port = settings.SUPABASE_PORT
    db = settings.SUPABASE_DB

    SQLALCHEMY_DATABASE_URL = f'postgresql://{user}:{password}@{host}:{port}/{db}'
    logger.debug(f'Connected to local Supabase at {SQLALCHEMY_DATABASE_URL}')

# Configure engine with connection pooling and prepared statement settings
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'connect_timeout': 5})


# Create the database tables
def create_db_and_tables() -> None:
    logger.info('Creating database tables if they do not exist...')
    SQLModel.metadata.create_all(engine)
    logger.info('Database setup complete.')


# Dependency to get the database session
def get_db_session() -> Generator[DBSession, Any, None]:
    logger.debug('Creating a new database session.')
    with DBSession(engine) as db_session:
        try:
            yield db_session
        finally:
            db_session.close()
            logger.debug('Database session closed.')
