from __future__ import annotations

from typing import TypeVar

from dotenv import load_dotenv
from google import genai
from google.genai.types import LiveConfig
from pydantic import BaseModel

from app.config import Settings

load_dotenv()

settings = Settings()
GEMINI_API_KEY = settings.GEMINI_API_KEY
ENABLE_AI = settings.ENABLE_AI
FORCE_CHEAP_MODEL = settings.FORCE_CHEAP_MODEL


DEFAULT_MODEL = 'gemini-2.0-flash-001'


live_config = LiveConfig(
    response_modalities=[LiveConfig.ResponseModality.AUDIO, LiveConfig.ResponseModality.TEXT],
    model=DEFAULT_MODEL,
)

client = genai.Client(api_key=GEMINI_API_KEY)


T = TypeVar('T', bound=BaseModel)


def get_client() -> genai.Client:
    """
    Returns the Gemini client instance.

    returns:
    - Gemini client instance
    """
    return client
