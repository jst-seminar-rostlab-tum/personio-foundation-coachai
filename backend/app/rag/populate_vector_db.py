"""Retrieval-augmented generation helpers for populate vector db."""

from pathlib import Path

from app.config import Settings
from app.connections.gemini_client import is_valid_api_key
from app.connections.vertexai_client import credentials
from app.rag.embeddings import get_embedding_model
from app.rag.rag import load_and_index_documents
from app.rag.vector_db import load_vector_db

settings = Settings()

TABLE_NAME = 'hr_information'
BASE_DIR = Path(__file__).parent
DOC_FOLDER = BASE_DIR / 'documents'
MODEL_TYPE = 'vertexai'


def populate_vector_db(doc_folder: str = DOC_FOLDER) -> None:
    """Populate the vector database with documents from a folder.

    Parameters:
        doc_folder (str): Directory containing documents to index.

    Returns:
        None: This function loads and indexes documents.
    """
    embedding = get_embedding_model(model_type=MODEL_TYPE)
    vector_db = load_vector_db(embedding)
    load_and_index_documents(vector_db, doc_folder)


if __name__ == '__main__':
    if MODEL_TYPE == 'vertexai' and not credentials:
        print(
            "Can't populate vector database. No valid VERTEX AI credentials available!"
            'Please update your .env and rerun the script'
        )
        exit()
    if MODEL_TYPE == 'gemini' and not is_valid_api_key(settings.GEMINI_API_KEY):
        print(
            "Can't populate vector database. No valid GEMINI API KEY available!"
            'Please update your .env and rerun the script'
        )
        exit()
    if not settings.SUPABASE_URL.strip():
        print(
            "Can't populate vector database. No SUPABASE URL available! "
            'Please update your .env and rerun the script'
        )
        exit()
    supabase_url = settings.SUPABASE_URL

    doc_folder_user = input(
        f'\nEnter the absolute path to the document directory (press Enter '
        f"for default '{DOC_FOLDER}'): "
    ).strip()
    if not doc_folder_user:
        doc_folder_user = DOC_FOLDER

    confirm = input(
        f'Do you want to proceed with this Supabase URL ({supabase_url})? (y/n): '
    ).strip()
    if confirm != 'y':
        print(
            'If you want to change the Supabase URL, '
            'please update your .env file and restart the script.'
        )
        exit()

    # Final configuration output
    print('\nUsing the following configuration:')
    print(f'Table Name: {TABLE_NAME}')
    print(f'Document Folder: {doc_folder_user}')
    print(f'Supabase URL: {supabase_url}')

    populate_vector_db(doc_folder=doc_folder_user)
