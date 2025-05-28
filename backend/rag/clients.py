import os

from dotenv import load_dotenv
from langchain_postgres import PGEngine
from supabase import Client, create_client

load_dotenv()


def get_supabase_client() -> Client:
    return create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))


def create_pg_engine() -> PGEngine:
    return PGEngine.from_params(
        database=os.getenv('PG_DB'),
        user=os.getenv('PG_USER'),
        password=os.getenv('PG_PASSWORD'),
        host=os.getenv('PG_HOST', 'localhost'),
        port=int(os.getenv('PG_PORT', 5432)),
    )


def get_db_client(backend: str) -> Client | PGEngine:
    if backend == 'supabase':
        return get_supabase_client()
    elif backend == 'postgres':
        return create_pg_engine()
    else:
        raise ValueError('Unsupported backend')
