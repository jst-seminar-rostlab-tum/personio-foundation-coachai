from __future__ import annotations

import logging
import os
from collections.abc import AsyncGenerator

from dotenv import load_dotenv
from google import genai
from google.genai.live import AsyncSession
from google.genai.types import LiveConnectConfig, Modality
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from app.config import Settings
from app.schemas.webrtc_schema import (
    GEMINI_SAMPLE_RATE,
    GeminiAudioChunk,
    GeminiAudioResponse,
    GeminiStreamConnectionError,
    GeminiStreamReceiveError,
    GeminiStreamSendError,
)
from app.services.audio_processor import opus_to_pcm, pcm_to_opus, resample_audio

logger = logging.getLogger(__name__)


load_dotenv()

settings = Settings()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
ENABLE_AI = settings.ENABLE_AI
FORCE_CHEAP_MODEL = settings.FORCE_CHEAP_MODEL


DEFAULT_MODEL = 'gemini-2.0-flash-001'


live_config = LiveConnectConfig(
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


class GeminiStreamManager:
    """
    The purpose of this class is to manage the session of
    audio stream from and to Gemini explicitly
    """

    def __init__(self) -> None:
        self.client = get_client()
        self.config = live_config
        self.session: AsyncSession | None = None
        self.is_connected = False

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(2),
        reraise=True,
        retry=retry_if_exception_type(GeminiStreamConnectionError),
    )
    async def create_session(self, peer_id: str) -> None:
        """Create a new session for the peer"""
        try:
            self.session = await self.client.aio.live.connect(
                model=DEFAULT_MODEL,
                config=self.config,
            )
            self.is_connected = True
            logger.info('Connected to Gemini Live API')
        except Exception as e:
            logger.error(f'Failed to connect to Gemini Live API: {e}')
            raise GeminiStreamConnectionError(
                f'Gemini connection failed: {e}', peer_id=peer_id
            ) from e

    async def close_session(self, peer_id: str) -> None:
        """Close the session for the peer"""
        if self.session:
            await self.session.close()
            self.is_connected = False
            logger.info('Disconnected from Gemini Live API')
        else:
            raise GeminiStreamConnectionError('Not connected to Gemini', peer_id=peer_id)

    async def send_audio(self, audio_chunk: GeminiAudioChunk, peer_id: str) -> None:
        """Send audio chunk to Gemini"""
        if not self.is_connected or not self.session:
            raise GeminiStreamConnectionError('Not connected to Gemini', peer_id=peer_id)

        try:
            # Process audio format
            pcm_data = opus_to_pcm(audio_chunk.data)
            resampled_data = resample_audio(pcm_data, audio_chunk.sample_rate, GEMINI_SAMPLE_RATE)

            # Send to Gemini
            await self.session.send(resampled_data, mime_type='audio/pcm')
            logger.debug(f'Sent audio chunk to Gemini: {len(resampled_data)} bytes')

        except Exception as e:
            logger.error(f'Error sending audio to Gemini: {e}')
            raise GeminiStreamSendError(f'Failed to send audio: {e}', peer_id=peer_id) from e

    async def receive_responses(self, peer_id: str) -> AsyncGenerator[GeminiAudioResponse, None]:
        """Receive responses from Gemini"""
        if not self.is_connected or not self.session:
            raise GeminiStreamConnectionError('Not connected to Gemini', peer_id=peer_id)

        try:
            async for response in self.session.receive():
                gemini_response = GeminiAudioResponse()

                # Process audio response
                if response.audio_data:
                    opus_data = pcm_to_opus(response.audio.data)
                    gemini_response.audio_data = opus_data

                # Process text response
                if response.transcript:
                    gemini_response.transcript = response.transcript
                    gemini_response.is_final = response.is_final

                yield gemini_response

        except Exception as e:
            logger.error(f'Error receiving from Gemini: {e}')
            raise GeminiStreamReceiveError(
                f'Failed to receive response: {e}', peer_id=peer_id
            ) from e
