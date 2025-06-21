from __future__ import annotations

import logging
import os

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

# 配置日志
logging.basicConfig(level=logging.INFO)

load_dotenv()

settings = Settings()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    logger.error('GEMINI_API_KEY not found in environment variables')
    raise GeminiStreamConnectionError('GEMINI_API_KEY not found in environment variables')

ENABLE_AI = settings.ENABLE_AI
FORCE_CHEAP_MODEL = settings.FORCE_CHEAP_MODEL

MODEL = 'models/gemini-2.0-flash-live-001'

if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
    logger.error('GOOGLE_APPLICATION_CREDENTIALS not found in environment variables')
    raise GeminiStreamConnectionError(
        'GOOGLE_APPLICATION_CREDENTIALS not found in environment variables'
    )

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


def get_client() -> genai.Client:
    if not hasattr(get_client, '_client'):
        try:
            logger.info('Creating Gemini client...')
            get_client._client = genai.Client(
                api_key=GEMINI_API_KEY,
                # http_options=HttpOptions(api_version='v1beta'),
            )
            logger.info('Gemini client created successfully')
        except Exception as e:
            logger.error(f'Failed to create Gemini client: {e}')
            raise GeminiStreamConnectionError(f'Failed to create Gemini client: {e}') from e
    return get_client._client


def generate_gemini_content(contents: list[str], model: str = MODEL) -> str:
    if not ENABLE_AI or get_client() is None:
        logger.error('Cannot upload files to Gemini, AI is disabled')
        return ''
    if None in contents:
        logger.error('None found in Gemini contents')
        return ''
    try:
        response = get_client().models.generate_content(model=model, contents=contents)
        return response.text
    except Exception as e:
        logger.error(f'Gemini content generation failed: {e}')


def upload_audio_gemini(audio_path: str) -> File:
    if not ENABLE_AI or get_client() is None:
        logger.error('Cannot upload files to Gemini, AI is disabled')
        return
    try:
        return get_client().files.upload(file=audio_path)
    except Exception as e:
        logger.error(f"Error uploading audio file '{audio_path}': {e}")
        return


def get_realtime_client() -> genai.Client:
    if not hasattr(get_realtime_client, '_client'):
        try:
            logger.info('Creating realtime Gemini client...')
            get_realtime_client._client = genai.Client(
                api_key=settings.GEMINI_API_KEY,
                http_options=HttpOptions(api_version='v1beta'),
            )
            logger.info('Realtime Gemini client created successfully')
        except Exception as e:
            logger.error(f'Failed to create realtime Gemini client: {e}')
            raise GeminiStreamConnectionError(
                f'Failed to create realtime Gemini client: {e}'
            ) from e
    return get_realtime_client._client
