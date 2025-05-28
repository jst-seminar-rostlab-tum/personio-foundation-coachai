import os

from clients import get_db_client
from embeddings import get_embedding_model
from langchain.embeddings.base import Embeddings
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.base import VectorStore, VectorStoreRetriever
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_postgres import PGEngine, PGVectorStore


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


async def initialize_vector_db(
    backend: str, documents: list[Document], embeddings: Embeddings, table_name: str
) -> VectorStore:
    db_client = get_db_client(backend)

    if not documents:
        raise ValueError('Cannot initialize vector DB with no documents.')

    if backend == 'supabase':
        return SupabaseVectorStore.from_documents(
            documents=documents,
            embedding=embeddings,
            client=db_client,
            table_name=table_name,
            query_name='match_documents',
            chunk_size=500,
        )
    elif backend == 'postgres':
        if not isinstance(db_client, PGEngine):
            raise TypeError('For PostgreSQL backend, db_client must be a PGEngine instance.')
        return await PGVectorStore.afrom_documents(
            documents=documents,
            embedding=embeddings,
            engine=db_client,
            table_name=table_name,
        )
    else:
        raise ValueError(f'Unsupported backend: {backend}')


async def get_vector_db_retriever(
    doc_folder: str = 'test_dir',
    db_backend: str = 'postgres',
    embedding_model_type: str = 'huggingface',
    table_name: str = 'test_tb',
) -> VectorStoreRetriever:
    docs = prepare_vector_db_docs(doc_folder=doc_folder)
    if not docs:
        raise ValueError(
            f'No documents processed from {doc_folder} to create a vector DB retriever.'
        )

    current_embeddings = get_embedding_model(model_type=embedding_model_type)

    vector_db = await initialize_vector_db(
        backend=db_backend, documents=docs, embeddings=current_embeddings, table_name=table_name
    )
    return vector_db.as_retriever()


def format_docs(docs: list[Document]) -> str:
    return '\n\n'.join([doc.page_content for doc in docs])


def load_vectorstore(
    backend: str, embedding: Embeddings, table_name: str, query_name: str = 'match_documents'
) -> VectorStore:
    db_client = get_db_client(backend)

    if backend == 'supabase':
        return SupabaseVectorStore(
            client=db_client,
            embedding=embedding,
            table_name=table_name,
            query_name=query_name,
        )
    elif backend == 'postgres':
        if not isinstance(db_client, PGEngine):
            raise TypeError('For PostgreSQL backend, db_client must be a PGEngine instance.')
        return PGVectorStore(engine=db_client, embedding=embedding, table_name=table_name)
    else:
        raise ValueError(f'Unsupported backend: {backend}')
