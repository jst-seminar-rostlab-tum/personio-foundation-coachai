from typing import Any

from google import genai
from google.genai.types import File

from app.config import Settings

settings = Settings()

DEFAULT_MODEL = 'gemini-2.0-flash'
GEMINI_API_KEY = settings.GEMINI_API_KEY


def _is_valid_api_key(key: str | None) -> bool:
    return bool(key and isinstance(key, str) and key.strip())


if not _is_valid_api_key(GEMINI_API_KEY):
    print(
        '[WARNING] GEMINI_API_KEY is missing or invalid. '
        'AI features will be disabled and mock responses will be used.'
    )
    ENABLE_AI = False
    gemini_client = None
else:
    ENABLE_AI = settings.ENABLE_AI
    gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)


def generate_gemini_content(contents: [Any], model: str = DEFAULT_MODEL) -> str:
    if not ENABLE_AI or gemini_client is None:
        return ''
    try:
        response = gemini_client.models.generate_content(model=model, contents=contents)
        return response.text
    except Exception as e:
        print(f'Gemini content generation failed: {e}')


def upload_audio_gemini(audio_path: str) -> File:
    if not ENABLE_AI or gemini_client is None:
        print('Cannot upload files to Gemini, AI is disabled')
    try:
        return gemini_client.files.upload(file=audio_path)
    except Exception as e:
        print(f"Error uploading audio file '{audio_path}': {e}")
