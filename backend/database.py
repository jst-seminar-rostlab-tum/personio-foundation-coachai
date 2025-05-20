from collections.abc import Generator
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from .config import settings

# SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}'

# SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}?sslmode=require"
# Database connection parameters


POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "zusjyx-Hedkyr-wevwi9"  # Replace [YOUR-PASSWORD] with the actual password
POSTGRES_HOST = "db.qgqfapwoopmzrkartwfw.supabase.co"
POSTGRES_PORT = "5432"
POSTGRES_DB = "postgres"
# user=postgres
# password=[YOUR-PASSWORD]
# host=db.qgqfapwoopmzrkartwfw.supabase.co
# port=5432
# dbname=postgres
# SQLAlchemy connection string
# SQLALCHEMY_DATABASE_URL = (
#     f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}?sslmode=require"
# )
SQLALCHEMY_DATABASE_URL = (
       "postgresql://postgres.syucjzgfvvmwsnairifl:fawgUs-9vujto-wyxgit@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"
    )
print(SQLALCHEMY_DATABASE_URL)
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, Any, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# from sqlalchemy import create_engine, MetaData
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.ext.declarative import declarative_base
# from dotenv import dotenv_values

# metadata = MetaData()
# Base = declarative_base()


# def db_connect():
#     # config = dotenv_values("./.env")
#     username = 'postgres'
#     password = 'fawgUs-9vujto-wyxgit'
#     dbname = 'postgres'
#     port = 5432
#     host = 'db.syucjzgfvvmwsnairifl.supabase.co' 
#     engine = create_engine(
#         "postgresql://postgres.syucjzgfvvmwsnairifl:fawgUs-9vujto-wyxgit@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"
#     )
#     connection = engine.connect()
#     print("Connected to the database")
#     return engine, connection


# def create_tables(engine):
#     metadata.drop_all(engine, checkfirst=True)
#     metadata.create_all(engine, checkfirst=True)


# def create_tables_orm(engine):
#     Base.metadata.drop_all(engine, checkfirst=True)
#     Base.metadata.create_all(engine, checkfirst=True)


# def create_session(engine):
#     Session = sessionmaker(bind=engine)
#     session = Session()
#     return session

# if __name__ == '__main__':
#     # Example usage
#     engine, conn = db_connect()
#     session = create_session(engine)
#     # Example test query
#     # result = conn.execute('SELECT current_date;')
#     # print(result.fetchone())
