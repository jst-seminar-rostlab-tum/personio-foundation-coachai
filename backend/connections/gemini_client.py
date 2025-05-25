import os
import threading

from dotenv import load_dotenv
from google import genai

load_dotenv()

_client = None
_client_lock = threading.Lock()


def init_gemini() -> None:
    """
    Initialize the Gemini client. This should be called once at app startup.
    If no key is provided, will use the GEMINI_API_KEY environment variable.
    """
    global _client
    with _client_lock:
        if _client is None:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError('GEMINI_API_KEY is required but not provided.')
            _client = genai.Client(api_key=api_key)


def get_client() -> genai.Client:
    """
    Return the initialized Gemini client instance.
    """
    if _client is None:
        raise RuntimeError('Gemini client is not initialized. Call init_gemini() first.')
    return _client
