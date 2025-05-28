import os
from pathlib import Path

from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from supabase import Client, create_client

load_dotenv()

BASE_DIR = Path(__file__).parent
PDF_PATH = BASE_DIR / 'documents' / 'Giving Feedback (CC BY-NC 4.0).pdf'

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
TABLE = 'hr_information'
QUERY_FN = 'match_documents'


def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    return GoogleGenerativeAIEmbeddings(
        model='models/embedding-001', google_api_key=os.getenv('GEMINI_API_KEY')
    )


def get_llm() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model='gemini-2.0-flash', google_api_key=os.getenv('GEMINI_API_KEY')
    )


def load_and_index_pdf() -> None:
    docs = PyPDFLoader(str(PDF_PATH)).load()
    chunks = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50).split_documents(docs)

    for doc in chunks:
        doc.metadata = {'metadata': doc.metadata}

    SupabaseVectorStore.from_documents(
        documents=chunks,
        embedding=get_embeddings(),
        client=get_supabase_client(),
        table_name=TABLE,
        query_name=QUERY_FN,
        chunk_size=500,
    )


def rag_chain() -> RetrievalQA:
    vectorstore = SupabaseVectorStore(
        client=get_supabase_client(),
        embedding=get_embeddings(),
        table_name=TABLE,
        query_name=QUERY_FN,
    )
    retriever = vectorstore.as_retriever(search_type='mmr', search_kwargs={'k': 5})
    return RetrievalQA.from_chain_type(llm=get_llm(), retriever=retriever, chain_type='stuff')


if __name__ == '__main__':
    load_and_index_pdf()
    chain = rag_chain()
    print(chain.invoke('What are barriers to effective feedback?'))
    print(
        """
Sources: 
Hardavella G, Aamli-Gaagnat A, Saad N, et al. 
How to give and receive feedback effectively. Breathe 2017; 13: 327–333
"""
    )
