import os
from pathlib import Path

from dotenv import load_dotenv
from embeddings import get_embedding_model
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableMap, RunnableSequence
from langchain_google_genai import ChatGoogleGenerativeAI
from vectorstore import format_docs, load_vectorstore, prepare_vector_db_docs

load_dotenv()

BASE_DIR = Path(__file__).parent
DOC_FOLDER = BASE_DIR / 'documents'

SUPABASE_BACKEND = 'supabase'
EMBEDDING_TYPE = 'gemini'
TABLE_NAME = 'hr_information'
QUERY_FN = 'match_documents'


def get_llm() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model='gemini-2.0-flash', google_api_key=os.getenv('GEMINI_API_KEY')
    )


def load_and_index_documents() -> None:
    os.makedirs(DOC_FOLDER, exist_ok=True)
    docs = prepare_vector_db_docs(str(DOC_FOLDER))
    if not docs:
        print(f'⚠️ No documents found in folder: {DOC_FOLDER}')
        return

    embedding = get_embedding_model(EMBEDDING_TYPE)
    vectorstore = load_vectorstore(SUPABASE_BACKEND, embedding, TABLE_NAME)
    vectorstore.add_documents(docs)
    print(f'Added {len(docs)} documents to vector store: {TABLE_NAME}')


def rag_chain() -> RunnableSequence:
    embedding = get_embedding_model(EMBEDDING_TYPE)
    vectorstore = load_vectorstore(SUPABASE_BACKEND, embedding, TABLE_NAME, query_name=QUERY_FN)
    retriever = vectorstore.as_retriever(search_type='mmr', search_kwargs={'k': 5})

    prompt = PromptTemplate.from_template(
        """
You are a concise assistant that gives an answer to a query based on the provided context.
Context: {context}
Query: {query}
Answer:

    """
    )

    return (
        RunnableMap(
            {
                'context': lambda x: format_docs(retriever.invoke(x['query'])),
                'query': lambda x: x['query'],
            }
        )
        | prompt
        | get_llm()
    )


if __name__ == '__main__':
    load_and_index_documents()
    chain = rag_chain()
    result = chain.invoke({'query': 'What are barriers to effective feedback?'})
    print(result.content)
    print(
        """
Sources: 
Hardavella G, Aamli-Gaagnat A, Saad N, et al. 
How to give and receive feedback effectively. Breathe 2017; 13: 327–333
"""
    )
