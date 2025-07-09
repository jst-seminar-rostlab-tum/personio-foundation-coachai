from typing import Any, TypeVar

from google import genai
from google.genai.types import GenerateContentConfig, Part
from google.oauth2 import service_account
from pydantic import BaseModel

from app.config import Settings

settings = Settings()

DEFAULT_CHEAP_MODEL = settings.DEFAULT_CHEAP_MODEL
DEFAULT_MODEL = settings.DEFAULT_MODEL
FORCE_CHEAP_MODEL = settings.FORCE_CHEAP_MODEL
VERTEXAI_PROJECT_ID = settings.VERTEXAI_PROJECT_ID
VERTEXAI_LOCATION = settings.VERTEXAI_LOCATION

required = [
    settings.GCP_PRIVATE_KEY_ID,
    settings.GCP_PRIVATE_KEY,
    settings.GCP_CLIENT_EMAIL,
    settings.GCP_CLIENT_ID,
]

try:
    if any(v in (None, '') for v in required):
        credentials = None
    else:
        creds_info = {
            'type': 'service_account',
            'project_id': settings.GCP_PROJECT_ID,
            'private_key_id': settings.GCP_PRIVATE_KEY_ID,
            'private_key': settings.GCP_PRIVATE_KEY.replace('\\n', '\n'),
            'client_email': settings.GCP_CLIENT_EMAIL,
            'client_id': settings.GCP_CLIENT_ID,
            'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
            'token_uri': 'https://oauth2.googleapis.com/token',
            'auth_provider_x509_cert_url': 'https://www.googleapis.com/oauth2/v1/certs',
            'client_x509_cert_url': f'https://www.googleapis.com/robot/v1/metadata/x509/{settings.GCP_CLIENT_EMAIL}',
            'universe_domain': 'googleapis.com',
        }

        credentials = service_account.Credentials.from_service_account_info(
            creds_info, scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
except Exception as e:
    credentials = None
    print(f'Failed to get service account credentials for Vertex AI: {e}')

if not credentials:
    print(
        '[WARNING] The Vertex AI credentials are missing or invalid. '
        'AI features will be disabled and mock responses will be used.'
    )
    ENABLE_AI = False
    vertexai_client = None
else:
    ENABLE_AI = settings.ENABLE_AI
    vertexai_client = genai.Client(
        credentials=credentials,
        vertexai=True,
        project=VERTEXAI_PROJECT_ID,
        location=VERTEXAI_LOCATION,
    )


def generate_content_vertexai(contents: [Any], model: str = DEFAULT_CHEAP_MODEL) -> str:
    if not ENABLE_AI or vertexai_client is None:
        print('Cannot upload files to Gemini on VertexAI, AI is disabled')
        return ''
    if None in contents:
        print('None found in Gemini on VertexAI contents')
        return ''
    try:
        response = vertexai_client.models.generate_content(model=model, contents=contents)
        return response.text
    except Exception as e:
        print(f'Gemini on VertexAI content generation failed: {e}')


def upload_audio_vertexai(audio_uri: str) -> Part:
    if not ENABLE_AI or vertexai_client is None:
        print('Cannot upload files to Gemini on VertexAI, AI is disabled')
    try:
        part = Part.from_uri(file_uri=audio_uri)
        return part
    except Exception as e:
        print(f"Error uploading audio file '{audio_uri}': {e}")


T = TypeVar('T', bound=BaseModel)


def call_llm_with_audio(
    request_prompt: str,
    audio_uri: str,
    system_prompt: str | None = None,
    model: str = DEFAULT_MODEL,
) -> str:
    if not ENABLE_AI or vertexai_client is None:
        return ''
    try:
        part = Part.from_uri(file_uri=audio_uri)
        selected_model = (
            DEFAULT_CHEAP_MODEL if FORCE_CHEAP_MODEL else (model or DEFAULT_CHEAP_MODEL)
        )
        response = vertexai_client.models.generate_content(
            model=selected_model,
            contents=[request_prompt, part],
            config=GenerateContentConfig(system_instruction=system_prompt),
        )

        if not response.text:
            return ''
        return response.text
    except Exception as e:
        print(f"Error uploading audio file '{audio_uri}': {e}")
        return ''


def call_structured_llm(
    request_prompt: str,
    output_model: type[T],
    system_prompt: str | None = None,
    model: str = DEFAULT_MODEL,
    temperature: float = 1,
    max_tokens: int = 500,
    mock_response: T | None = None,
) -> T:
    if not ENABLE_AI or vertexai_client is None:
        if not mock_response:
            raise ValueError('AI is disabled and no mock response provided')
        return mock_response

    selected_model = DEFAULT_CHEAP_MODEL if FORCE_CHEAP_MODEL else (model or DEFAULT_CHEAP_MODEL)
    response = vertexai_client.models.generate_content(
        model=selected_model,
        contents=request_prompt,
        config=GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=temperature,
            max_output_tokens=max_tokens,
            response_schema=output_model,
            response_mime_type='application/json',
        ),
    )

    if not response.text:
        raise ValueError('Gemini on VertexAI did not return a valid response')

    json_response = response.text
    return output_model.model_validate_json(json_response)
