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

from .embeddings import get_embedding_model
from .vector_db import (
    format_docs,
    load_vector_db,
    prepare_vector_db_docs,
)

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


def load_and_index_documents(vector_db: SupabaseVectorStore) -> None:
    os.makedirs(DOC_FOLDER, exist_ok=True)
    docs = prepare_vector_db_docs(str(DOC_FOLDER))
    if not docs:
        print(f'⚠️ No documents found in folder: {DOC_FOLDER}')
        return

    vector_db.add_documents(docs)
    print(f'Added {len(docs)} documents to vector store: {TABLE_NAME}')


def build_vector_db_retriever(populate_db: bool) -> VectorStoreRetriever:
    embedding = get_embedding_model(EMBEDDING_TYPE)
    vector_db = load_vector_db(embedding, TABLE_NAME)
    if populate_db:
        load_and_index_documents(vector_db)
    retriever = vector_db.as_retriever(search_type=SEARCH_TYPE, search_kwargs={'k': K_SEARCH})
    return retriever


def get_llm() -> ChatGoogleGenerativeAI:
    if not settings.gemini_api_key:
        raise ValueError('Missing GEMINI_API_KEY in environment')
    return ChatGoogleGenerativeAI(model='gemini-2.0-flash', google_api_key=settings.gemini_api_key)


def rag_chain(
    populate_db: bool = DEFAULT_POPULATE_DB,
    prompt: str = DEFAULT_PROMPT,
) -> RunnableSerializable[Any, BaseMessage]:
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
    chain = rag_chain(populate_db=True)
    result = chain.invoke({'query': query})
    print(result.content)
    print(
        """
        Sources: 
        Hardavella G, Aamli-Gaagnat A, Saad N, et al. 
        How to give and receive feedback effectively. Breathe 2017; 13: 327–333
        """
    )
