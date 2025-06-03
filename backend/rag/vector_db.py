import os

from langchain.embeddings.base import Embeddings
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import SupabaseVectorStore
from supabase import Client, create_client

from backend.config import Settings

settings = Settings()


def prepare_vector_db_docs(doc_folder: str) -> list[Document]:
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = []
    if not os.path.isdir(doc_folder):
        print(f"Warning: Document folder '{doc_folder}' does not exist.")
        return []
    for file in os.listdir(doc_folder):
        if file.endswith('.pdf'):
            file_path = os.path.join(doc_folder, file)
            try:
                loader = PyPDFLoader(file_path)
                doc = loader.load()
                splits = text_splitter.split_documents(doc)
                docs.extend(splits)
            except Exception as e:
                print(f'Error loading or splitting PDF {file_path}: {e}')
    return docs


def format_docs(docs: list[Document]) -> str:
    return '\n\n'.join([doc.page_content for doc in docs])


def get_supabase_client() -> Client:
    return create_client(
        f'https://{settings.supabase_project_id}.supabase.co', settings.supabase_key
    )


def load_vector_db(
    embedding: Embeddings, table_name: str, query_name: str = 'match_documents'
) -> SupabaseVectorStore:
    db_client = get_supabase_client()

    return SupabaseVectorStore(
        client=db_client,
        embedding=embedding,
        table_name=table_name,
        query_name=query_name,
    )
