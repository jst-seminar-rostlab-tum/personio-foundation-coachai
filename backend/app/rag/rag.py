import os
from pathlib import Path
from typing import Any

from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_core.messages import BaseMessage
from langchain_core.runnables import (
    RunnableLambda,
    RunnableSerializable,
)
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import Settings
from app.rag.embeddings import get_embedding_model
from app.rag.vector_db import format_docs, load_vector_db, prepare_vector_db_docs

BASE_DIR = Path(__file__).parent
DOC_FOLDER = BASE_DIR / 'documents'

settings = Settings()


EMBEDDING_TYPE = 'gemini'
TABLE_NAME = 'hr_information'
SEARCH_TYPE = 'mmr'
K_SEARCH = 5
DEFAULT_PROMPT = """
        You are a concise assistant that gives an answer to a query based on the provided context.
        Context: {context}
        Query: {query}
        Answer:
        """
DEFAULT_POPULATE_DB = False


def load_and_index_documents(
    vector_db: SupabaseVectorStore, doc_folder: str = DOC_FOLDER, table_name: str = TABLE_NAME
) -> None:
    """
    Loads and indexes PDF documents from the configured folder into the provided vector store.

    This function:
    - Ensures the document folder exists.
    - Loads and splits documents into smaller chunks.
    - Adds them to the given SupabaseVectorStore instance.

    Parameters:
        vector_db (SupabaseVectorStore): The vector store where documents will be added.
        doc_folder (str): The folder where the documents are stored.
    """
    os.makedirs(doc_folder, exist_ok=True)
    docs = prepare_vector_db_docs(str(doc_folder))
    if not docs:
        print(f'⚠️ No documents found in folder: {doc_folder}')
        return

    vector_db.add_documents(docs)
    print(f'Added {len(docs)} documents to vector store: {table_name}')


def build_vector_db_retriever(
    populate_db: bool = DEFAULT_POPULATE_DB,
) -> VectorStoreRetriever:
    """
    Builds a vector-based retriever using the specified embedding model
    and vector store configuration.

    If `populate_db` is set, documents are loaded and indexed before constructing the retriever.

    Parameters:
        populate_db (bool): Whether to load and index documents into the vector DB.

    Returns:
        VectorStoreRetriever: A retriever instance for querying the vector database.
    """
    embedding = get_embedding_model(EMBEDDING_TYPE)
    vector_db = load_vector_db(embedding, TABLE_NAME)
    if populate_db:
        load_and_index_documents(vector_db)
    retriever = vector_db.as_retriever(search_type=SEARCH_TYPE, search_kwargs={'k': K_SEARCH})
    return retriever


def get_llm() -> ChatGoogleGenerativeAI:
    """
    Initializes and returns a Gemini Chat LLM client using the API key from settings.

    Returns:
        ChatGoogleGenerativeAI: An instance of the Gemini chat model.

    Raises:
        ValueError: If the GEMINI_API_KEY is missing in the environment.
    """
    if not settings.GEMINI_API_KEY:
        raise ValueError('Missing GEMINI_API_KEY in environment')
    return ChatGoogleGenerativeAI(model='gemini-2.0-flash', google_api_key=settings.GEMINI_API_KEY)


def rag_chain(
    populate_db: bool = DEFAULT_POPULATE_DB,
    prompt: str = DEFAULT_PROMPT,
) -> RunnableSerializable[Any, BaseMessage]:
    """
    Constructs a Retrieval-Augmented Generation (RAG) chain using a LLM
    and vector retriever.

    This pipeline:
    - Retrieves relevant documents from the vector DB using a retriever.
    - Formats the context and query into a prompt.
    - Passes the prompt to the Gemini LLM for response generation.

    Parameters:
        populate_db (bool): Whether to populate the vector database at initialization.
        prompt (str): The prompt template used to guide the LLM's response.

    Returns:
        RunnableSerializable[Any, BaseMessage]: A LangChain Runnable representing
        the full RAG pipeline.
    """
    llm = get_llm()
    retriever = build_vector_db_retriever(populate_db)
    prompt = PromptTemplate.from_template(prompt)

    return (
        RunnableLambda(
            lambda x: {'context': format_docs(retriever.invoke(x['query'])), 'query': x['query']}
        )
        | prompt
        | llm
    )


if __name__ == '__main__':
    query = 'What are barriers to effective feedback?'
    chain = rag_chain(
        # Uncomment to populate db (if vector db is emtpy)
        # populate_db=True,
    )
    result = chain.invoke({'query': query})
    print(result.content)
    print(
        """
        Sources: 
        Hardavella G, Aamli-Gaagnat A, Saad N, et al. 
        How to give and receive feedback effectively. Breathe 2017; 13: 327–333
        """
    )
