from typing import Any

from google import genai
from google.genai.types import File

from app.config import Settings

settings = Settings()

DEFAULT_MODEL = 'gemini-2.0-flash'
gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)


def generate_gemini_content(contents: [Any], model: str = DEFAULT_MODEL) -> str:
    try:
        response = gemini_client.models.generate_content(model=model, contents=contents)
        return response.text
    except Exception as e:
        print(f'Gemini content generation failed: {e}')


def upload_audio_gemini(audio_path: str) -> File:
    try:
        return gemini_client.files.upload(file=audio_path)
    except Exception as e:
        print(f"Error uploading audio file '{audio_path}': {e}")
