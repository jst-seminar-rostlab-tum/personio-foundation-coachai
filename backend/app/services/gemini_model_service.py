import asyncio
import contextlib
import logging
import re
from abc import abstractmethod
from collections.abc import AsyncGenerator, AsyncIterator
from typing import Optional, Protocol, Union

from aiortc import RTCDataChannel, RTCPeerConnection
from av import AudioFrame, AudioResampler
from google import genai
from google.genai import live
from PIL.Image import Image

from app.connections.gemini_client import LIVE_CONFIG, MODEL, get_client
from app.schemas.webrtc_schema import (
    GeminiStreamConnectionError,
    GeminiStreamReceiveError,
    GeminiStreamSendError,
)

SAMPLE_RATE = 16000
AUDIO_PTIME = 0.02

type Input = Union[str, AudioFrame, Image]
type Output = AudioFrame

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


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


class TranscriptionProcessor:
    def __init__(self) -> None:
        self.buffer = ''

    def _process_text(self, text: str) -> str:
        # 1. Remove extra spaces and line breaks
        text = text.replace('\n', ' ').replace('\r', '').strip()
        text = re.sub(r'\s+', ' ', text)

        # 2. Add space after punctuation
        text = re.sub(r'([.,!?])([A-Za-z])', r'\1 \2', text)

        # 3. Add space before capital letters at sentence start
        text = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', text)

        # 4. Fix common word joins
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)

        return text.strip()

    def _split_sentences(self, text: str) -> tuple[list[str], str]:
        # Split by sentence endings
        sentences = re.split(r'([.!?])\s*', text)
        result = []
        current = ''

        for i in range(0, len(sentences) - 1, 2):
            if i + 1 < len(sentences):
                current += sentences[i] + sentences[i + 1]
                if sentences[i + 1] in '.!?':
                    result.append(current.strip())
                    current = ''
            else:
                current += sentences[i]

        return result, current

    def process_text(self, text: str) -> Optional[str]:
        if not text:
            return None

        # logger.debug(f'Processing text: {text}')
        self.buffer += text
        # logger.debug(f'Current buffer: {self.buffer}')

        # Process text
        processed_buffer = self._process_text(self.buffer)
        # logger.debug(f'Processed buffer: {processed_buffer}')

        # Split sentences
        complete_sentences, remaining = self._split_sentences(processed_buffer)
        # logger.debug(f'Complete sentences: {complete_sentences}')
        # logger.debug(f'Remaining text: {remaining}')

        if complete_sentences:
            self.buffer = remaining
            return ' '.join(complete_sentences)

        return None

    def flush(self) -> Optional[str]:
        if self.buffer.strip():
            result = self._process_text(self.buffer)
            # logger.debug(f'Flush result: {result}')
            self.buffer = ''
            return result
        return None

    def clear(self) -> None:
        self.buffer = ''


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
        self._output_transcription_queue = asyncio.Queue()
        self._input_transcription_queue = asyncio.Queue()
        self._output_processor = TranscriptionProcessor()
        self._input_processor = TranscriptionProcessor()
        self._input = ''
        self._output = ''

        self.turn_queue = asyncio.Queue()

    async def send(self, input: Input) -> None:
        try:
            if isinstance(input, str):
                await self.session.send(input=input, end_of_turn=True)
            elif isinstance(input, AudioFrame):
                for frame in self.resampler.resample(input):
                    blob = genai.types.BlobDict(
                        data=frame.to_ndarray().tobytes(),
                        mime_type=f'audio/pcm;rate={SAMPLE_RATE}',
                    )
                    await self.session.send(input=blob)
        except Exception as e:
            logger.error(f'Error sending to Gemini: {e}')
            raise GeminiStreamSendError(f'Error sending to Gemini: {e}') from e

    async def recv(self) -> AsyncIterator[Output]:
        """Only process audio frames"""
        try:
            turn = self.session.receive()
            async for response in turn:
                if data := response.data:
                    self.turn_queue.put_nowait(data)
                    print(f'{self.turn_queue.qsize()} items in turn queue')

                if response.server_content.turn_complete:
                    logger.info('Turn complete')

                if response.server_content.interrupted:
                    logger.info('Turn interrupted')
                    break

                if response.data is not None:
                    mime_type = response.server_content.model_turn.parts[0].inline_data.mime_type
                    sample_rate = int(mime_type.split('rate=')[1])

                    frame = AudioFrame(format='s16', layout='mono', samples=len(response.data) / 2)
                    frame.sample_rate = sample_rate
                    frame.planes[0].update(response.data)
                    yield frame

            assert response.server_content is not None
            if (
                response.server_content.output_transcription
                and response.server_content.output_transcription.text
            ):
                transcription = response.server_content.output_transcription
                logger.debug(f'Received transcription: {transcription}')
                processed_text = self._output_processor.process_text(transcription.text)
                finished = transcription.finished
                if processed_text:
                    logger.debug(f'Sending processed text: {processed_text}')
                    self._output += processed_text
                if finished:
                    await self._output_transcription_queue.put(self._output)
                    self._output = ''
                    self._output_processor.clear()
            if (
                response.server_content.input_transcription
                and response.server_content.input_transcription.text
            ):
                transcription = response.server_content.input_transcription
                logger.debug(f'Received input transcription: {transcription}')
                processed_text = self._input_processor.process_text(transcription.text)
                finished = transcription.finished
                if processed_text:
                    logger.debug(f'Sending processed text: {processed_text}')
                    self._input += processed_text
                if finished:
                    await self._input_transcription_queue.put(self._input)
                    self._input = ''
                    self._input_processor.clear()
            if response.server_content.generation_complete or response.server_content.interrupted:
                logger.debug('Generation complete')
                output_final_text = self._output_processor.flush()
                if output_final_text:
                    self._output += output_final_text
                input_final_text = self._input_processor.flush()
                if input_final_text:
                    self._input += input_final_text
                await self._output_transcription_queue.put_nowait(self._output)
                await self._input_transcription_queue.put_nowait(self._input)
                self._input = ''
                self._output = ''
        except Exception as e:
            logger.error(f'Error receiving from Gemini: {e}')
            raise GeminiStreamReceiveError(f'Error receiving from Gemini: {e}') from e

        while not self._audio_queue.empty():
            print('Clearing audio queue')
            self._audio_queue.get_nowait()

    async def audio_receiver(self) -> None:
        """Receives from Gemini and puts audio and transcriptions in queues."""
        while True:
            turn = self.session.receive()
            async for response in turn:
                if data := response.data:
                    await self._audio_queue.put((data, response))
                    logger.debug(f'{self._audio_queue.qsize()} items in audio queue')

                assert response.server_content is not None

                if response.server_content.turn_complete:
                    logger.info('Turn complete')

                if response.server_content.interrupted:
                    logger.info('Turn interrupted')
                if response.server_content.output_transcription:
                    transcription = response.server_content.output_transcription
                    processed_text = self._output_processor.process_text(transcription.text)
                    finished = transcription.finished
                    logger.debug(f'Output finished: {finished}')
                    if processed_text:
                        logger.debug(f'Sending processed text: {processed_text}')
                        self._output += processed_text
                    if finished:
                        await self._output_transcription_queue.put(self._output)
                        logger.debug(
                            f'Output transcription queue'
                            f'size: {self._output_transcription_queue.qsize()}'
                        )
                        self._output = ''
                if response.server_content.input_transcription:
                    transcription = response.server_content.input_transcription
                    processed_text = self._input_processor.process_text(transcription.text)
                    finished = transcription.finished
                    logger.debug(f'Input finished: {finished}')
                    if processed_text:
                        logger.debug(f'Sending processed text: {processed_text}')
                        self._input += processed_text
                    if finished:
                        await self._input_transcription_queue.put(self._input)
                        logger.debug(
                            f'Input transcription queue'
                            f'size: {self._input_transcription_queue.qsize()}'
                        )
                        self._input = ''
                        self._input_processor.clear()
                if response.server_content.turn_complete or response.server_content.interrupted:
                    logger.debug('Generation complete')
                    self._output_processor.clear()
                    self._input_processor.clear()
                    await self._output_transcription_queue.put(self._output)
                    await self._input_transcription_queue.put(self._input)
                    self._input = ''
                    self._output = ''

            # Clean up audio queue
            while not self._audio_queue.empty():
                logger.debug('Clearing audio queue')
                self._audio_queue.get_nowait()

    async def audio_frame_consumer(self) -> AsyncIterator[AudioFrame]:
        """Yields AudioFrame objects as they become available."""
        while True:
            data, response = await self._audio_queue.get()
            mime_type = response.server_content.model_turn.parts[0].inline_data.mime_type
            sample_rate = int(mime_type.split('rate=')[1])
            frame = AudioFrame(format='s16', layout='mono', samples=len(data) // 2)
            frame.sample_rate = sample_rate
            frame.planes[0].update(data)
            yield frame

    async def close(self) -> None:
        if self.session is None:
            return
        await self.session.close()
        self.session = None

        input_final_text = self._input_processor.flush()
        if input_final_text:
            self._input += input_final_text
        output_final_text = self._output_processor.flush()
        if output_final_text:
            self._output += output_final_text
        self._input = ''
        self._output = ''


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
            gemini = Gemini(session)
            # Start background task here, if you want
            # gemini.audio_task = asyncio.create_task(gemini.audio_receiver())
            yield gemini
    except Exception as e:
        logger.error(f'Failed to connect to Gemini: {e}')
        raise GeminiStreamConnectionError(f'Failed to connect to Gemini: {e}') from e
