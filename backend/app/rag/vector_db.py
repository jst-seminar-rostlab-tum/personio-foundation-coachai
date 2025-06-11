import os

from langchain.embeddings.base import Embeddings
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import SupabaseVectorStore
from supabase import Client, create_client

from app.config import Settings

settings = Settings()


def prepare_vector_db_docs(doc_folder: str) -> list[Document]:
    """
    Loads and splits PDF documents from a specified folder for vector database ingestion.

    Each PDF is processed using LangChain's PyPDFLoader and split into smaller chunks using
    RecursiveCharacterTextSplitter to prepare for embedding and storage.

    Parameters:
        doc_folder (str): The path to the folder containing PDF documents.

    Returns:
        list[Document]: A list of text-split Document objects ready for embedding.

    Notes:
        - Non-PDF files are ignored.
        - Errors during loading or splitting are caught and printed.
        - Returns an empty list if the folder does not exist.
    """
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
    """
    Formats a list of Document objects into a single string, joining their contents.

    Parameters:
        docs (list[Document]): A list of LangChain Document objects.

    Returns:
        str: A single string containing the concatenated contents of all documents,
             separated by double newlines.
    """
    return '\n\n'.join([doc.page_content for doc in docs])


def get_supabase_client() -> Client:
    """
    Initializes and returns a Supabase client using credentials from settings.

    Returns:
        Client: An authenticated Supabase client instance.
    """
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


def load_vector_db(
    embedding: Embeddings, table_name: str, query_name: str = 'match_documents'
) -> SupabaseVectorStore:
    """
    Initializes a SupabaseVectorStore with the given embedding model and configuration.

    Parameters:
        embedding (Embeddings): The embedding model to use for vector operations.
        table_name (str): The name of the Supabase table used for storing vectors.
        query_name (str): The name of the stored procedure or query for similarity search
                          (default is 'match_documents').

    Returns:
        SupabaseVectorStore: A vector store instance connected to the specified Supabase table.
    """
    db_client = get_supabase_client()

    return SupabaseVectorStore(
        client=db_client,
        embedding=embedding,
        table_name=table_name,
        query_name=query_name,
    )
