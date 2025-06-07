from __future__ import annotations

import logging
import os

from dotenv import load_dotenv
from google import genai
from google.genai.types import LiveConnectConfig, Modality

from app.config import Settings
from app.schemas.webrtc_schema import GeminiStreamConnectionError

logger = logging.getLogger(__name__)


load_dotenv()

settings = Settings()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
ENABLE_AI = settings.ENABLE_AI
FORCE_CHEAP_MODEL = settings.FORCE_CHEAP_MODEL


DEFAULT_MODEL = 'gemini-2.0-flash-001'


LIVE_CONFIG = LiveConnectConfig(
    response_modalities=[Modality.AUDIO],
    temperature=None,
)


def get_client() -> genai.Client:
    if not hasattr(get_client, '_client'):
        try:
            get_client._client = genai.Client(api_key=GEMINI_API_KEY)
        except Exception as e:
            logger.error(f'Failed to create Gemini client: {e}')
            raise GeminiStreamConnectionError(f'Failed to create Gemini client: {e}') from e
    return get_client._client
