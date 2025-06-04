from langchain.embeddings.base import Embeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings

from app.config import Settings

settings = Settings()


def get_embedding_model(model_type: str = 'huggingface') -> Embeddings:
    if model_type == 'gemini':
        return GoogleGenerativeAIEmbeddings(
            model='models/embedding-001', google_api_key=settings.gemini_api_key
        )
    elif model_type == 'huggingface':
        return HuggingFaceEmbeddings(model_name='sentence-transformers/all-mpnet-base-v2')
    else:
        raise ValueError(f'Unsupported embedding model: {model_type}')
