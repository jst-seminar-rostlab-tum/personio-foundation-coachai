import asyncio
import contextlib
import logging
from abc import abstractmethod
from collections.abc import AsyncGenerator, AsyncIterator
from typing import Optional, Protocol, Union

from aiortc import RTCDataChannel, RTCPeerConnection
from av import AudioFrame, AudioResampler
from google import genai
from google.genai import live
from PIL.Image import Image

from app.connections.gemini_client import LIVE_CONFIG, MODEL, get_client

SAMPLE_RATE = 16000
AUDIO_PTIME = 0.02

type Input = Union[str, AudioFrame, Image]
type Output = AudioFrame

# 配置日志
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class RTCConnection(Protocol):
    datachannel: Optional[RTCDataChannel]
    pc: Optional[RTCPeerConnection]


class Model(Protocol):
    @abstractmethod
    async def send(self, _input: Input) -> None:
        pass

    @abstractmethod
    async def recv(self) -> AsyncIterator[Output]:
        pass

    @abstractmethod
    async def close(self) -> None:
        pass


class Gemini(Model):
    def __init__(
        self,
        session: live.AsyncSession,
    ) -> None:
        self.session = session
        self.resampler = AudioResampler(
            format='s16',
            layout='mono',
            rate=SAMPLE_RATE,
            frame_size=int(SAMPLE_RATE * AUDIO_PTIME),
        )
        self._audio_queue = asyncio.Queue()
        self._transcription_queue = asyncio.Queue()

    async def send(self, input: Input) -> None:
        if isinstance(input, str):
            await self.session.send(input=input, end_of_turn=True)
        elif isinstance(input, AudioFrame):
            for frame in self.resampler.resample(input):
                blob = genai.types.BlobDict(
                    data=frame.to_ndarray().tobytes(),
                    mime_type=f'audio/pcm;rate={SAMPLE_RATE}',
                )
                await self.session.send(input=blob)

    async def recv(self) -> AsyncIterator[Output]:
        """Only process audio frames"""
        turn = self.session.receive()
        async for response in turn:
            if response.data is not None:
                mime_type = response.server_content.model_turn.parts[0].inline_data.mime_type
                sample_rate = int(mime_type.split('rate=')[1])

                frame = AudioFrame(format='s16', layout='mono', samples=len(response.data) / 2)
                frame.sample_rate = sample_rate
                frame.planes[0].update(response.data)
                yield frame

            if (
                response.server_content.output_transcription
                and response.server_content.output_transcription.text
            ):
                await self._transcription_queue.put(
                    response.server_content.output_transcription.text
                )

    async def process_transcriptions(self) -> None:
        """Process transcription text asynchronously"""
        while True:
            try:
                transcription = await self._transcription_queue.get()
                logger.info(f'Processing transcription: {transcription}')
                # TODO: Add text processing logic here
            except Exception as e:
                logger.error(f'Error processing transcription: {e}')

    async def close(self) -> None:
        if self.session is None:
            return
        await self.session.close()
        self.session = None


client = get_client()


@contextlib.asynccontextmanager
async def connect_gemini() -> AsyncGenerator[Gemini, None]:
    try:
        logger.info('Connecting to Gemini...')
        async with client.aio.live.connect(
            model=MODEL,
            config=LIVE_CONFIG,
        ) as session:
            logger.info('Connected to Gemini successfully')
            yield Gemini(session)
    except Exception as e:
        logger.error(f'Failed to connect to Gemini: {e}')
        raise e
