from backend.config import Settings
from google import genai

settings = Settings()

client = genai.Client(api_key=settings.GENAI_API_KEY)


def generate_llm_content(prompt: str, model: str = 'gemini-2.0-flash') -> str:
    response = client.models.generate_content(model=model, contents=prompt)
    return response.text
