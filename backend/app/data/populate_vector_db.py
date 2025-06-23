from pathlib import Path

from app.config import Settings
from app.connections.gemini_client import is_valid_api_key
from app.rag.embeddings import get_embedding_model
from app.rag.rag import load_and_index_documents
from app.rag.vector_db import load_vector_db

settings = Settings()

EMBEDDING_TYPE = 'gemini'
TABLE_NAME = 'hr_information'
BASE_DIR = Path(__file__).parent
DOC_FOLDER = BASE_DIR / 'documents'


def populate_vector_db(table_name: str = TABLE_NAME, doc_folder: str = DOC_FOLDER) -> None:
    embedding = get_embedding_model(EMBEDDING_TYPE)
    vector_db = load_vector_db(embedding, table_name)
    load_and_index_documents(vector_db, doc_folder, table_name)


if __name__ == '__main__':
    if not is_valid_api_key(settings.GEMINI_API_KEY):
        print(
            "Can't populate vector database. No valid GEMINI API KEY available! "
            'Please update your .env and rerun the script'
        )
        exit()
    if not settings.SUPABASE_URL or len(settings.SUPABASE_URL) == 0:
        print(
            "Can't populate vector database. No SUPABASE URL available! "
            'Please update your .env and rerun the script'
        )
        exit()
    supabase_url = settings.SUPABASE_URL

    table_name_user = input(
        "Enter the table name (press Enter for default 'hr_information'): "
    ).strip()
    if not table_name_user:
        table_name_user = 'hr_information'

    doc_folder_user = input(
        f"Enter the path to the document directory (press Enter for default '{DOC_FOLDER}'): "
    ).strip()
    if not doc_folder_user:
        doc_folder_user = '/documents'

    # Show Supabase URL from environment and confirm
    print(f"\nSupabase URL from settings: '{supabase_url}'")
    confirm = input('Do you want to proceed with this Supabase URL? (y/n): ').strip().lower()
    if confirm != 'y':
        print(
            'If you want to change the Supabase URL, '
            'please update your .env file and restart the script.'
        )
        exit()

    # Final configuration output
    print('\nUsing the following configuration:')
    print(f'Table Name: {table_name_user}')
    print(f'Document Folder: {doc_folder_user}')
    print(f'Supabase URL: {supabase_url}')

    populate_vector_db()
