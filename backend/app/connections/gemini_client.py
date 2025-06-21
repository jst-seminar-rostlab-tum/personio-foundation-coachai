from __future__ import annotations

import contextlib
import logging
import os
from collections.abc import AsyncGenerator

from dotenv import load_dotenv
from google import genai
from google.genai.types import (
    AutomaticActivityDetection,
    Content,
    ContextWindowCompressionConfig,
    EndSensitivity,
    File,
    HttpOptions,
    LiveConnectConfig,
    MediaResolution,
    Modality,
    Part,
    PrebuiltVoiceConfig,
    RealtimeInputConfig,
    SlidingWindow,
    SpeechConfig,
    StartSensitivity,
    VoiceConfig,
)

from app.config import Settings
from app.schemas.webrtc_schema import GeminiStreamConnectionError

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

load_dotenv()

settings = Settings()

# The API key is no longer needed, as authentication will be handled by the
# service account specified in the GOOGLE_APPLICATION_CREDENTIALS environment variable.
# GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
#
# if not GEMINI_API_KEY:
#     logger.error('GEMINI_API_KEY not found in environment variables')
#     raise GeminiStreamConnectionError('GEMINI_API_KEY not found in environment variables')

ENABLE_AI = settings.ENABLE_AI
FORCE_CHEAP_MODEL = settings.FORCE_CHEAP_MODEL

MODEL = 'models/gemini-2.0-flash-live-001'

if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
    logger.error('GOOGLE_APPLICATION_CREDENTIALS not found in environment variables')
    raise GeminiStreamConnectionError(
        'GOOGLE_APPLICATION_CREDENTIALS not found in environment variables'
    )


# This check is no longer needed. The client will be initialized using
# Application Default Credentials.
# def _is_valid_api_key(key: str | None) -> bool:
#     return bool(key and isinstance(key, str) and key.strip())
#
#
# if not _is_valid_api_key(GEMINI_API_KEY):
#     print(
#         '[WARNING] GEMINI_API_KEY is missing or invalid. '
#         'AI features will be disabled and mock responses will be used.'
#     )
#     ENABLE_AI = False
#     gemini_client = None
# else:
#     ENABLE_AI = settings.ENABLE_AI
#     gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)
try:
    gemini_client = genai.Client()
    ENABLE_AI = settings.ENABLE_AI
except Exception as e:
    logger.warning(
        f'[WARNING] Failed to initialize Gemini client, likely due to missing credentials: {e}. '
        'AI features will be disabled and mock responses will be used.'
    )
    ENABLE_AI = False
    gemini_client = None


def generate_gemini_content(contents: list[str], model: str = MODEL) -> str:
    if not ENABLE_AI or gemini_client is None:
        logger.error('Cannot upload files to Gemini, AI is disabled')
        return ''
    if None in contents:
        logger.error('None found in Gemini contents')
        return ''
    try:
        response = gemini_client.models.generate_content(model=model, contents=contents)
        return response.text
    except Exception as e:
        logger.error(f'Gemini content generation failed: {e}')


def upload_audio_gemini(audio_path: str) -> File:
    if not ENABLE_AI or gemini_client is None:
        logger.error('Cannot upload files to Gemini, AI is disabled')
    try:
        return gemini_client.files.upload(file=audio_path)
    except Exception as e:
        logger.error(f"Error uploading audio file '{audio_path}': {e}")


LIVE_CONFIG = LiveConnectConfig(
    system_instruction=Content(
        parts=[
            Part(
                text='You are a helpful assistant. '
                + 'Wait for the user to speak first before responding. '
                + 'Only respond when the user has finished speaking. '
                + 'Do not start the conversation yourself.'
            )
        ]
    ),
    media_resolution=MediaResolution.MEDIA_RESOLUTION_MEDIUM,
    response_modalities=[Modality.AUDIO],
    speech_config=SpeechConfig(
        voice_config=VoiceConfig(prebuilt_voice_config=PrebuiltVoiceConfig(voice_name='Fenrir')),
        language_code='en-US',  # TODO: set in user interface
        # Supported languages: https://ai.google.dev/gemini-api/docs/live#supported-languages
    ),
    realtime_input_config=RealtimeInputConfig(
        automatic_activity_detection=AutomaticActivityDetection(
            disabled=False,  # default
            start_of_speech_sensitivity=StartSensitivity.START_SENSITIVITY_LOW,
            end_of_speech_sensitivity=EndSensitivity.END_SENSITIVITY_HIGH,
            prefix_padding_ms=20,
            silence_duration_ms=100,
        ),
    ),
    context_window_compression=ContextWindowCompressionConfig(
        trigger_tokens=25600,
        sliding_window=SlidingWindow(target_tokens=12800),
    ),
    input_audio_transcription={},
    output_audio_transcription={},
)


def get_realtime_client() -> genai.Client:
    if not hasattr(get_realtime_client, '_client'):
        try:
            logger.info('Creating Gemini client...')
            # The api_key parameter is removed to allow the client to use Application
            # Default Credentials.
            get_realtime_client._client = genai.Client(
                http_options=HttpOptions(api_version='v1beta'),
            )
            logger.info('Gemini client created successfully')
        except Exception as e:
            logger.error(f'Failed to create Gemini client: {e}')
            raise GeminiStreamConnectionError(f'Failed to create Gemini client: {e}') from e
    return get_realtime_client._client


@contextlib.asynccontextmanager
async def connect_realtime_gemini() -> AsyncGenerator[genai.Client, None]:
    """
    Connect to Gemini realtime session and configure it
    Yield the connection object.
    """
    client = get_realtime_client()
    try:
        async with client.aio.live.connect(
            model=MODEL,
            config=LIVE_CONFIG,
        ) as session:
            yield session
    except Exception as e:
        logger.error(f'Failed to connect to Gemini: {e}')
        raise GeminiStreamConnectionError(f'Failed to connect to Gemini: {e}') from e
