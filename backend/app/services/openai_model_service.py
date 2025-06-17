import asyncio
import base64
import contextlib
import logging
import re
from collections.abc import AsyncGenerator, AsyncIterator
from typing import Optional, Union

from av import AudioFrame, AudioResampler
from openai import AsyncOpenAI
from openai.types.beta import realtime as openai_types

from app.connections.openai_client import connect_realtime_openai

SAMPLE_RATE = 24000
AUDIO_PTIME = 0.02

Input = Union[str, AudioFrame]
Output = AudioFrame

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


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

    def process_text_chunked(self, text: str) -> list[str]:
        """Process text chunked - output chunks at sentence endings"""
        if not text:
            return []

        # Add new text to buffer
        self.buffer += text
        processed_buffer = self._process_text(self.buffer)

        # Find complete sentences
        complete_sentences, remaining = self._split_sentences(processed_buffer)

        chunks = []
        if complete_sentences:
            # Only output complete sentences
            for sentence in complete_sentences:
                if sentence.strip():
                    chunks.append(sentence.strip())

            # Update buffer, keep incomplete parts
            self.buffer = remaining

        return chunks

    def process_text(self, text: str) -> Optional[str]:
        """Original complete sentence processing logic"""
        if not text:
            return None

        self.buffer += text
        processed_buffer = self._process_text(self.buffer)

        # Split sentences
        complete_sentences, remaining = self._split_sentences(processed_buffer)

        if complete_sentences:
            self.buffer = remaining
            return ' '.join(complete_sentences)

        return None

    def flush(self) -> Optional[str]:
        """Output all remaining text"""
        if self.buffer.strip():
            result = self._process_text(self.buffer)
            self.buffer = ''
            return result
        return None

    def clear(self) -> None:
        self.buffer = ''


class OpenAIRealtime:
    def __init__(self, session: openai_types.Session) -> None:
        self.session: openai_types.Session = session
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
        self._is_interrupted = False

    async def send(self, input: Input) -> None:
        try:
            if isinstance(input, str):
                await self.session.conversation.item.create(
                    item={
                        'type': 'message',
                        'role': 'user',
                        'content': [{'type': 'input_text', 'text': input}],
                    }
                )
                await self.session.response.create()
            elif isinstance(input, AudioFrame):
                for frame in self.resampler.resample(input):
                    data = frame.to_ndarray().tobytes()
                    audio = base64.b64encode(data).decode('utf-8')
                    await self.session.input_audio_buffer.append(audio=audio)
        except Exception as e:
            logger.error(f'Error sending to OpenAI: {e}')
            raise e

    async def recv(self) -> AsyncIterator[Output]:
        """Only process audio frames"""
        try:
            async for event in self.session:
                if event.type == 'response.audio.delta':
                    # Only process audio if not interrupted
                    if not self._is_interrupted:
                        data = base64.b64decode(event.delta)

                        frame = AudioFrame(format='s16', layout='mono', samples=len(data) // 2)
                        frame.sample_rate = SAMPLE_RATE
                        frame.planes[0].update(data)

                        yield frame

                # Set interruption flag when user starts speaking
                elif event.type == 'input_audio_buffer.speech_started':
                    logger.info('User speech detected in recv - setting interruption flag')
                    self._is_interrupted = True

                # Process input audio transcription completed event
                elif event.type == 'conversation.item.input_audio_transcription.completed':
                    if hasattr(event, 'transcript') and event.transcript:
                        processed_text = self._input_processor.process_text(event.transcript)
                        if processed_text:
                            await self._input_transcription_queue.put(processed_text)
                            logger.debug(f'Input transcription: {processed_text}')

                    # Reset interruption state
                    self._is_interrupted = False

                # Process response audio transcription - only process if not interrupted
                elif event.type == 'response.output_item.done':
                    if not self._is_interrupted and (
                        hasattr(event, 'item')
                        and hasattr(event.item, 'content')
                        and event.item.content
                    ):
                        for content_part in event.item.content:
                            if (
                                hasattr(content_part, 'type')
                                and content_part.type == 'audio'
                                and hasattr(content_part, 'transcript')
                                and content_part.transcript
                            ):
                                processed_text = self._output_processor.process_text(
                                    content_part.transcript
                                )
                                if processed_text:
                                    await self._output_transcription_queue.put(processed_text)
                                    logger.debug(f'Output transcription: {processed_text}')
                    elif self._is_interrupted:
                        logger.debug('Skipping output transcription in recv due to interruption')

                elif event.type == 'response.done':
                    logger.info('Response complete')
                    # Clear processors for next round of conversation
                    self._output_processor.clear()
                    self._input_processor.clear()

        except Exception as e:
            logger.error(f'Error receiving from OpenAI: {e}')
            raise e

        while not self._audio_queue.empty():
            logger.debug('Clearing audio queue')
            self._audio_queue.get_nowait()

    async def audio_receiver(self) -> None:
        """Receives from OpenAI and puts audio and transcriptions in queues."""
        try:
            async for event in self.session:
                if event.type == 'response.audio.delta':
                    # Only add audio data if not interrupted
                    if not self._is_interrupted:
                        data = base64.b64decode(event.delta)
                        await self._audio_queue.put(data)

                # Automatic interruption: clear audio queue and set
                # interruption flag when user starts speaking
                elif event.type == 'input_audio_buffer.speech_started':
                    logger.info('User speech detected - interrupting response')
                    self._is_interrupted = True
                    # Clear audio queue to implement interruption effect
                    while not self._audio_queue.empty():
                        try:
                            self._audio_queue.get_nowait()
                        except asyncio.QueueEmpty:
                            break
                    logger.debug('Audio queue cleared and transcription stopped due to user speech')

                # Process input audio transcription completed event
                elif event.type == 'conversation.item.input_audio_transcription.completed':
                    if hasattr(event, 'transcript') and event.transcript:
                        logger.debug(f'Input transcription completed: {event.transcript}')
                        processed_text = self._input_processor.process_text(event.transcript)
                        if processed_text:
                            await self._input_transcription_queue.put(processed_text)
                            logger.debug(f'Input transcription: {processed_text}')

                    # Reset interruption state, prepare to process new response
                    self._is_interrupted = False
                    logger.debug('Interruption state reset')

                # Process response audio transcription - only process if not interrupted
                elif event.type == 'response.output_item.done':
                    if not self._is_interrupted and (
                        hasattr(event, 'item')
                        and hasattr(event.item, 'content')
                        and event.item.content
                    ):
                        for content_part in event.item.content:
                            if (
                                hasattr(content_part, 'type')
                                and content_part.type == 'audio'
                                and hasattr(content_part, 'transcript')
                                and content_part.transcript
                            ):
                                logger.debug(f'Output transcription: {content_part.transcript}')
                                processed_text = self._output_processor.process_text(
                                    content_part.transcript
                                )
                                if processed_text:
                                    await self._output_transcription_queue.put(processed_text)
                                    logger.debug(f'Output transcription: {processed_text}')
                    elif self._is_interrupted:
                        logger.debug('Skipping output transcription due to interruption')

                elif event.type == 'response.done':
                    logger.info('Response complete')
                    # Clear processors for next round of conversation
                    self._output_processor.clear()
                    self._input_processor.clear()

            # Clean up audio queue if interrupted
            if self._is_interrupted:
                while not self._audio_queue.empty():
                    logger.debug('Clearing audio queue due to interruption')
                    self._audio_queue.get_nowait()

        except asyncio.CancelledError:
            logger.info('audio_receiver task cancelled')
            raise
        except Exception as e:
            logger.error(f'Error in audio receiver: {e}')
            raise e

    async def audio_frame_consumer(self) -> AsyncIterator[AudioFrame]:
        """Yields AudioFrame objects as they become available."""
        try:
            while True:
                try:
                    # Use timeout to avoid infinite waiting
                    data = await asyncio.wait_for(self._audio_queue.get(), timeout=1.0)
                    frame = AudioFrame(format='s16', layout='mono', samples=len(data) // 2)
                    frame.sample_rate = SAMPLE_RATE
                    frame.planes[0].update(data)
                    yield frame
                except TimeoutError:
                    continue
                except asyncio.CancelledError:
                    logger.info('audio_frame_consumer cancelled')
                    break
        except Exception as e:
            logger.error(f'Error in audio frame consumer: {e}')
            raise e

    async def close(self) -> None:
        logger.info('Closing OpenAI session')
        if self.session is None:
            return

        try:
            # Set timeout to avoid infinite waiting
            await asyncio.wait_for(self.session.close(), timeout=2.0)
        except TimeoutError:
            logger.warning('OpenAI session close timed out')
        except Exception as e:
            logger.error(f'Error closing OpenAI session: {e}')
        finally:
            self.session = None

        # Clear processors
        try:
            self._input_processor.clear()
            self._output_processor.clear()
        except Exception as e:
            logger.error(f'Error clearing processors: {e}')


client = AsyncOpenAI()


@contextlib.asynccontextmanager
async def connect_openai() -> AsyncGenerator[OpenAIRealtime, None]:
    async with connect_realtime_openai() as conn:
        yield OpenAIRealtime(conn)
