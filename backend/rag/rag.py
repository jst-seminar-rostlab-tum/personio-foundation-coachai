import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from embeddings import get_embedding_model
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_core.messages import BaseMessage
from langchain_core.runnables import (
    RunnableLambda,
    RunnableSerializable,
)
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_google_genai import ChatGoogleGenerativeAI
from vector_db import format_docs, load_vector_db, prepare_vector_db_docs

load_dotenv()

BASE_DIR = Path(__file__).parent
DOC_FOLDER = BASE_DIR / 'documents'

EMBEDDING_TYPE = 'gemini'
TABLE_NAME = 'hr_information'
QUERY_FN = 'match_documents'
SEARCH_TYPE = 'mmr'
K_SEARCH = 5
default_prompt = """
        You are a concise assistant that gives an answer to a query based on the provided context.
        Context: {context}
        Query: {query}
        Answer:
        """


def load_and_index_documents(vector_db: SupabaseVectorStore) -> None:
    os.makedirs(DOC_FOLDER, exist_ok=True)
    docs = prepare_vector_db_docs(str(DOC_FOLDER))
    if not docs:
        print(f'⚠️ No documents found in folder: {DOC_FOLDER}')
        return

    vector_db.add_documents(docs)
    print(f'Added {len(docs)} documents to vector store: {TABLE_NAME}')


def get_vector_db_retriever() -> VectorStoreRetriever:
    embedding = get_embedding_model(EMBEDDING_TYPE)
    vector_db = load_vector_db(embedding, TABLE_NAME, query_name=QUERY_FN)
    load_and_index_documents(vector_db)
    retriever = vector_db.as_retriever(search_type=SEARCH_TYPE, search_kwargs={'k': K_SEARCH})
    return retriever


def get_llm() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model='gemini-2.0-flash', google_api_key=os.getenv('GEMINI_API_KEY')
    )


def rag_chain(prompt: str = default_prompt) -> RunnableSerializable[Any, BaseMessage]:
    llm = get_llm()
    retriever = get_vector_db_retriever()
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
    chain = rag_chain()
    result = chain.invoke({'query': query})
    print(result.content)
    print(
        """
        Sources: 
        Hardavella G, Aamli-Gaagnat A, Saad N, et al. 
        How to give and receive feedback effectively. Breathe 2017; 13: 327–333
        """
    )
