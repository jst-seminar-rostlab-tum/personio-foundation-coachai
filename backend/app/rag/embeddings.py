from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_openai import OpenAIEmbeddings

from app.config import Settings
from app.connections.vertexai_client import credentials

settings = Settings()


def get_embedding_model(
    model_type: str = 'vertexai',
) -> VertexAIEmbeddings | GoogleGenerativeAIEmbeddings | OpenAIEmbeddings:
    """
    Returns an embedding model instance based on the specified provider.

    Supported model types:
    - 'gemini': Uses GoogleGenerativeAIEmbeddings with the Gemini API.
    More suitable for low to medium user traffic
    - 'openai': Uses OpenAIEmbeddings with the OpenAI API.
    More suitable for high user traffic

    Parameters:
        model_type (str): The embedding provider to use.
        Must be 'gemini' or 'openai' (default: 'gemini').

    Returns:
        Embeddings: An instance of a LangChain-compatible embedding model.

    Raises:
        ValueError: If an unsupported model type is specified.
    """
    if model_type == 'vertexai':
        if not credentials:
            raise ValueError('No VertexAI Credentials to create embedding model')
        return VertexAIEmbeddings(model_name='text-embedding-005', credentials=credentials)
    elif model_type == 'gemini':
        if not settings.GEMINI_API_KEY:
            raise ValueError('No GEMINI_API_KEY to create embedding model')
        return GoogleGenerativeAIEmbeddings(
            model='models/embedding-001', google_api_key=settings.GEMINI_API_KEY
        )
    elif model_type == 'openai':
        if not settings.OPENAI_API_KEY:
            raise ValueError('No OPENAI_API_KEY to create embedding model')
        return OpenAIEmbeddings(
            model='text-embedding-3-small', openai_api_key=settings.OPENAI_API_KEY
        )
    else:
        raise ValueError(f'Unsupported embedding model: {model_type}')
