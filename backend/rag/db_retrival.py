import os

from langchain.vectorstores.base import VectorStoreRetriever
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres import PGEngine, PGVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter

# It seems like (https://github.com/langchain-ai/langchain-postgres) PGVectorStore > PGVector

embeddings_model = HuggingFaceEmbeddings(model_name='sentence-transformers/all-mpnet-base-v2')


def create_engine() -> PGEngine:
    # TODO: Implement
    # Tutorial here: https://github.com/langchain-ai/langchain-postgres/blob/main/examples/pg_vectorstore.ipynb
    return None


def prepare_vector_db_docs(doc_folder: str) -> list[Document]:
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = []
    for file in os.listdir(doc_folder):
        file_path = os.path.join(doc_folder, file)
        loader = PyPDFLoader(file_path)
        doc = loader.load()
        splits = text_splitter.split_documents(doc)
        docs.extend(splits)
    return docs


def initialize_vector_db(
        documents: list[Document],
        embeddings: HuggingFaceEmbeddings,
        engine: PGEngine,
        table_name: str) -> PGVectorStore:
    # Source:
    # https://python.langchain.com/api_reference/postgres/v2/langchain_postgres.v2.vectorstores.PGVectorStore.html
    vector_db = PGVectorStore.afrom_documents(
        documents=documents,
        embedding=embeddings,
        engine=engine,
        table_name=table_name,
    )
    return vector_db


def get_vector_db_retriever() -> VectorStoreRetriever:
    # TODO: Implement getting vector_db by loading, not only instantiating
    docs = prepare_vector_db_docs(doc_folder="test_dir")
    engine = create_engine()
    vector_db = initialize_vector_db(documents=docs,
                                     embeddings=embeddings_model,
                                     engine=engine,
                                     table_name="test_tb")
    retriever = vector_db.as_retriever()
    return retriever


def format_docs(docs: list[Document]) -> str:
    return "\n\n".join([doc.content for doc in docs])
