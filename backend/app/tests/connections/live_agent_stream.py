"""
## Documentation

Local WebRTC audio stream simulator,
based on WebRTC service architecture but using pyaudio

Includes comprehensive event system for monitoring:
- Audio events: stream start/end, voice activity, silence detection
- Session events: session lifecycle, Gemini connection status
- Data channel events: transcript handling, message passing

## Setup

To install the dependencies for this script, run:

```
pip install google-genai pyaudio
```

## Event System Usage

The local audio loop supports event handlers for monitoring various aspects:

```python
# Create audio loop
audio_loop = (
    LocalAudioLoop(
        peer_id
    )
)

# Add event handlers
audio_loop.add_audio_event_handler(
    my_audio_handler
)
audio_loop.add_session_event_handler(
    my_session_handler
)
audio_loop.add_data_channel_event_handler(
    my_data_handler
)
```

Event types include:
- LocalAudioEventType: AUDIO_STREAM_START, AUDIO_STREAM_END,
    VOICE_ACTIVITY_DETECTED, SILENCE_DETECTED, AUDIO_QUALITY_CHANGED
- LocalSessionEventType: SESSION_STARTED, SESSION_ENDED, GEMINI_CONNECTED,
    GEMINI_DISCONNECTED, SESSION_ERROR
- LocalDataChannelEventType: CHANNEL_READY, TRANSCRIPT_SENT, MESSAGE_RECEIVED
"""

import asyncio
import contextlib
import logging
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from enum import Enum
from typing import Generic, TypeVar

import pyaudio
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.live import AsyncSession

from app.connections.gemini_client import LIVE_CONFIG, MODEL, get_client
from app.services.audio_processor import (
    CHANNELS,
    CHUNK_SIZE,
    RECEIVE_SAMPLE_RATE,
    SEND_SAMPLE_RATE,
    is_silence,
    resample_pcm_audio,
)
from app.services.webrtc_service import SendToGeminiType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

FORMAT = pyaudio.paInt16

TranscriptCallback = Callable[[str, str], Awaitable[None]]

client = get_client()
pya = pyaudio.PyAudio()


# Event System
class LocalAudioEventType(Enum):
    """Local audio event types"""

    AUDIO_STREAM_START = 'audio_stream_start'
    AUDIO_STREAM_END = 'audio_stream_end'
    VOICE_ACTIVITY_DETECTED = 'voice_activity_detected'
    SILENCE_DETECTED = 'silence_detected'
    AUDIO_QUALITY_CHANGED = 'audio_quality_changed'


class LocalSessionEventType(Enum):
    """Local session event types"""

    SESSION_STARTED = 'session_started'
    SESSION_ENDED = 'session_ended'
    SESSION_ERROR = 'session_error'
    GEMINI_CONNECTED = 'gemini_connected'
    GEMINI_DISCONNECTED = 'gemini_disconnected'


class LocalDataChannelEventType(Enum):
    """Local data channel event types (simulated)"""

    CHANNEL_READY = 'channel_ready'
    CHANNEL_CLOSED = 'channel_closed'
    TRANSCRIPT_SENT = 'transcript_sent'
    MESSAGE_RECEIVED = 'message_received'


T = TypeVar('T')


@dataclass
class LocalAudioEvent(Generic[T]):
    """Local audio event"""

    type: LocalAudioEventType
    peer_id: str
    data: T | None = None
    timestamp: float = None

    def __post_init__(self) -> None:
        if self.timestamp is None:
            self.timestamp = time.time()


@dataclass
class LocalSessionEvent(Generic[T]):
    """Local session event"""

    type: LocalSessionEventType
    peer_id: str
    data: T = None  # type: ignore
    timestamp: float = None

    def __post_init__(self) -> None:
        if self.timestamp is None:
            self.timestamp = time.time()


@dataclass
class LocalDataChannelEvent(Generic[T]):
    """Local data channel event (simulated)"""

    type: LocalDataChannelEventType
    peer_id: str
    data: T = None  # type: ignore
    timestamp: float = None

    def __post_init__(self) -> None:
        if self.timestamp is None:
            self.timestamp = time.time()


# Event callbacks
LocalAudioEventCallback = Callable[[LocalAudioEvent[T]], Awaitable[None]]
LocalSessionEventCallback = Callable[[LocalSessionEvent[T]], Awaitable[None]]
LocalDataChannelEventCallback = Callable[[LocalDataChannelEvent[T]], Awaitable[None]]


class LocalEventManager(Generic[T]):
    """Local event manager for handling audio, session, and data channel events"""

    def __init__(self, peer_id: str) -> None:
        self.peer_id = peer_id
        self.audio_event_handlers: list[LocalAudioEventCallback[T]] = []
        self.session_event_handlers: list[LocalSessionEventCallback[T]] = []
        self.data_channel_event_handlers: list[LocalDataChannelEventCallback[T]] = []

    def add_audio_event_handler(self, handler: LocalAudioEventCallback[T]) -> None:
        self.audio_event_handlers.append(handler)

    def add_session_event_handler(self, handler: LocalSessionEventCallback[T]) -> None:
        self.session_event_handlers.append(handler)

    def add_data_channel_event_handler(self, handler: LocalDataChannelEventCallback[T]) -> None:
        self.data_channel_event_handlers.append(handler)

    async def emit_audio_event(
        self, event_type: LocalAudioEventType, data: T | None = None
    ) -> None:
        event = LocalAudioEvent(type=event_type, peer_id=self.peer_id, data=data)
        logger.debug(
            f'[EventManager] Emitting audio event {event_type.value} for peer {self.peer_id}'
        )
        for handler in self.audio_event_handlers:
            try:
                await handler(event)
            except Exception as e:
                logger.error(f'[EventManager] Error in audio event handler: {e}')

    async def emit_session_event(
        self, event_type: LocalSessionEventType, data: T | None = None
    ) -> None:
        event = LocalSessionEvent(type=event_type, peer_id=self.peer_id, data=data)
        logger.debug(
            f'[EventManager] Emitting session event {event_type.value} for peer {self.peer_id}'
        )
        for handler in self.session_event_handlers:
            try:
                await handler(event)
            except Exception as e:
                logger.error(f'[EventManager] Error in session event handler: {e}')

    async def emit_data_channel_event(
        self, event_type: LocalDataChannelEventType, data: T | None = None
    ) -> None:
        event = LocalDataChannelEvent(type=event_type, peer_id=self.peer_id, data=data)
        logger.debug(
            f'[EventManager] Emitting data channel event {event_type.value} for peer {self.peer_id}'
        )
        for handler in self.data_channel_event_handlers:
            try:
                await handler(event)
            except Exception as e:
                logger.error(f'[EventManager] Error in data channel event handler: {e}')


@dataclass
class LocalPeer:
    """
    LocalPeer is a local peer, similar to the Peer in WebRTC.
    It has an audio_stream_in and audio_stream_out, and an audio_loop.
    The audio_loop is a LocalAudioLoop.
    """

    peer_id: str
    audio_stream_in: pyaudio.Stream | None = None
    audio_stream_out: pyaudio.Stream | None = None
    audio_loop: 'LocalAudioLoop | None' = None

    async def cleanup(self) -> None:
        """
        Cleanup all resources.
        """
        if self.audio_loop:
            await self.audio_loop.stop()
        if self.audio_stream_in:
            self.audio_stream_in.stop_stream()
            self.audio_stream_in.close()
        if self.audio_stream_out:
            self.audio_stream_out.stop_stream()
            self.audio_stream_out.close()


class LocalAudioLoop:
    """
    LocalAudioLoop is a local audio loop, similar to the WebRTCAudioLoop.
    It has an audio_in_queue and an audio_out_queue.
    The audio_in_queue is a queue of audio data from Gemini.
    The audio_out_queue is a queue of audio data to Gemini.
    """

    def __init__(self, peer_id: str) -> None:
        self.peer_id = peer_id

        # Audio queues, similar to the WebRTC queues.
        self.audio_in_queue: asyncio.Queue[types.Blob] | None = None  # Audio from Gemini.
        self.audio_out_queue: asyncio.Queue[types.Blob] | None = None  # Audio to Gemini.

        # Task management
        self._main_task: asyncio.Task | None = None

        # Local audio device
        self.peer: LocalPeer | None = None

        # Gemini session management
        self.gemini_client: genai.Client = get_client()
        self.gemini_session: AsyncSession | None = None

        # Transcript callback
        self.on_transcript_callback: TranscriptCallback | None = None

        # Voice activity detection
        self.last_voice_time = time.time()
        self.silence_timeout = 1.0
        self._is_voice_active = False  # Track voice activity state

        # Simulated data channel ready state
        self._data_channel_ready = asyncio.Event()
        self._pending_transcripts: list[str] = []

        # Event management
        self.event_manager = LocalEventManager(peer_id)

    def set_transcript_callback(self, callback: TranscriptCallback) -> None:
        """Set the transcript callback."""
        self.on_transcript_callback = callback

    def add_audio_event_handler(self, handler: LocalAudioEventCallback) -> None:
        """Add audio event handler"""
        self.event_manager.add_audio_event_handler(handler)

    def add_session_event_handler(self, handler: LocalSessionEventCallback) -> None:
        """Add session event handler"""
        self.event_manager.add_session_event_handler(handler)

    def add_data_channel_event_handler(self, handler: LocalDataChannelEventCallback) -> None:
        """Add data channel event handler"""
        self.event_manager.add_data_channel_event_handler(handler)

    def mark_data_channel_ready(self) -> None:
        """Mark the data channel ready (simulated)."""
        logger.info(f'[LocalAudioLoop] Simulated data channel ready for peer {self.peer_id}')
        self._data_channel_ready.set()

        # Emit data channel ready event
        asyncio.create_task(
            self.event_manager.emit_data_channel_event(
                LocalDataChannelEventType.CHANNEL_READY,
                {'message': 'Data channel simulation ready'},
            )
        )

        # Send pending transcripts
        if self._pending_transcripts and self.on_transcript_callback:
            logger.info(f'for peer {self.peer_id}')
            asyncio.create_task(self._send_pending_transcripts())

    async def _send_pending_transcripts(self) -> None:
        """Send all pending transcripts."""
        if not self.on_transcript_callback:
            return

        for transcript in self._pending_transcripts:
            try:
                await self.on_transcript_callback(transcript, self.peer_id)
            except Exception as e:
                logger.error(
                    f'[LocalAudioLoop] Error sending pending transcripts '
                    f'for peer {self.peer_id}: {e}'
                )

        self._pending_transcripts.clear()
        logger.info(f'[LocalAudioLoop] All pending transcripts sent for peer {self.peer_id}')

    async def start(self, peer: LocalPeer) -> None:
        """Start the audio stream processing."""
        self.peer = peer

        # Initialize queues
        self.audio_in_queue = asyncio.Queue[types.Blob]()
        self.audio_out_queue = asyncio.Queue[types.Blob](maxsize=5)

        # Emit session started event
        await self.event_manager.emit_session_event(
            LocalSessionEventType.SESSION_STARTED, {'message': 'Local audio session started'}
        )

        # Setup audio streams
        await self._setup_audio_streams()

        # Emit audio stream start event
        await self.event_manager.emit_audio_event(
            LocalAudioEventType.AUDIO_STREAM_START, {'message': 'Audio stream setup completed'}
        )

        # Start main task
        self._main_task = asyncio.create_task(self._run_with_gemini())

        logger.info(f'LocalAudioLoop started successfully for peer {self.peer_id}')

    async def _setup_audio_streams(self) -> None:
        """Setup audio input and output streams."""
        try:
            # Get default input device
            mic_info = pya.get_default_input_device_info()

            # Setup input stream
            self.peer.audio_stream_in = await asyncio.to_thread(
                pya.open,
                format=FORMAT,
                channels=CHANNELS,
                rate=SEND_SAMPLE_RATE,
                input=True,
                input_device_index=mic_info['index'],
                frames_per_buffer=CHUNK_SIZE,
            )

            # Setup output stream
            self.peer.audio_stream_out = await asyncio.to_thread(
                pya.open,
                format=FORMAT,
                channels=CHANNELS,
                rate=RECEIVE_SAMPLE_RATE,
                output=True,
            )

            logger.info(f'Audio stream setup successfully for peer {self.peer_id}')

        except Exception as e:
            logger.error(f'Failed to setup audio stream for peer {self.peer_id}: {e}')
            raise

    async def _run_with_gemini(self) -> None:
        """Run the audio task with Gemini session."""
        try:
            async with (
                self.gemini_client.aio.live.connect(model=MODEL, config=LIVE_CONFIG) as session,
                asyncio.TaskGroup() as tg,
            ):
                self.gemini_session = session
                logger.info(f'[Gemini] Session started for peer {self.peer_id}')

                # Emit Gemini connected event
                await self.event_manager.emit_session_event(
                    LocalSessionEventType.GEMINI_CONNECTED,
                    {'message': 'Connected to Gemini Live API'},
                )

                # Send welcome message
                await self._send_to_gemini(
                    types.Content(
                        role='user',
                        parts=[types.Part(text='Hello! I am ready to chat.')],
                    )
                )

                # Start all tasks
                tg.create_task(self._listen_local_audio())
                tg.create_task(self._send_realtime())
                tg.create_task(self._play_local_audio())
                tg.create_task(self._receive_audio_from_gemini())

                # Keep session active
                await asyncio.sleep(float('inf'))

        except asyncio.CancelledError:
            logger.info(f'[Gemini] Session cancelled for peer {self.peer_id}')
            await self.event_manager.emit_session_event(
                LocalSessionEventType.GEMINI_DISCONNECTED,
                {'message': 'Gemini session cancelled by user'},
            )
        except Exception as e:
            logger.error(f'[Gemini] Session error for peer {self.peer_id}: {e}', exc_info=True)
            await self.event_manager.emit_session_event(
                LocalSessionEventType.SESSION_ERROR,
                {'error': str(e), 'message': 'Gemini session error'},
            )
        finally:
            self.gemini_session = None
            logger.info(f'[Gemini] Session ended for peer {self.peer_id}')
            await self.event_manager.emit_session_event(
                LocalSessionEventType.GEMINI_DISCONNECTED, {'message': 'Gemini session ended'}
            )

    async def stop(self) -> None:
        """Stop the audio stream processing."""
        # Emit session ending event
        await self.event_manager.emit_session_event(
            LocalSessionEventType.SESSION_ENDED, {'message': 'Local audio session ending'}
        )

        # Emit audio stream end event
        await self.event_manager.emit_audio_event(
            LocalAudioEventType.AUDIO_STREAM_END, {'message': 'Audio stream stopped'}
        )

        if self._main_task:
            self._main_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._main_task
            self._main_task = None

        # Clear queues
        if self.audio_in_queue:
            while not self.audio_in_queue.empty():
                try:
                    self.audio_in_queue.get_nowait()
                except asyncio.QueueEmpty:
                    break

        logger.info(f'LocalAudioLoop stopped for peer {self.peer_id}')

    async def _listen_local_audio(self) -> None:
        """Listen to local audio input."""
        try:
            if not self.peer or not self.peer.audio_stream_in:
                logger.error(f'No audio input stream for peer {self.peer_id}')
                return

            kwargs = {'exception_on_overflow': False} if __debug__ else {}

            while True:
                # Read audio data
                data = await asyncio.to_thread(self.peer.audio_stream_in.read, CHUNK_SIZE, **kwargs)

                data = resample_pcm_audio(
                    data,
                    source_sample_rate=self.peer.audio_stream_in._rate,
                    target_sample_rate=SEND_SAMPLE_RATE,
                    channels=CHANNELS,
                )

                # Check if it's silence
                if not data or len(data) < 320 or is_silence(data):
                    # Emit silence detected event if voice was previously active
                    if self._is_voice_active:
                        self._is_voice_active = False
                        await self.event_manager.emit_audio_event(
                            LocalAudioEventType.SILENCE_DETECTED,
                            {
                                'message': 'Voice activity stopped',
                                'duration': time.time() - self.last_voice_time,
                            },
                        )

                    if (
                        self.gemini_session
                        and time.time() - self.last_voice_time > self.silence_timeout
                    ):
                        # Send audio stream end signal (simulated)
                        self.last_voice_time = time.time()
                    continue

                # Voice activity detected
                if not self._is_voice_active:
                    self._is_voice_active = True
                    await self.event_manager.emit_audio_event(
                        LocalAudioEventType.VOICE_ACTIVITY_DETECTED,
                        {'message': 'Voice activity started', 'audio_length': len(data)},
                    )

                self.last_voice_time = time.time()

                # Put audio data into queue
                if self.audio_out_queue:
                    await self.audio_out_queue.put(types.Blob(data=data, mime_type='audio/pcm'))

        except Exception as e:
            logger.error(f'Error listening to local audio for peer {self.peer_id}: {e}')

    async def _send_realtime(self) -> None:
        """Send audio to Gemini."""
        try:
            while self.audio_out_queue:
                audio_msg = await self.audio_out_queue.get()
                await self._send_to_gemini(audio_msg)
                logger.debug(f'[LocalAudio] Audio sent to Gemini for peer {self.peer_id}')
        except Exception as e:
            logger.error(f'Error sending audio to Gemini for peer {self.peer_id}: {e}')

    async def _play_local_audio(self) -> None:
        """Play local audio output."""
        try:
            if not self.peer or not self.peer.audio_stream_out:
                logger.error(f'No audio output stream for peer {self.peer_id}')
                return

            while self.audio_in_queue:
                # Get PCM data
                pcm_data = await self.audio_in_queue.get()

                pcm_data.data = resample_pcm_audio(
                    pcm_data.data,
                    source_sample_rate=RECEIVE_SAMPLE_RATE,
                    target_sample_rate=self.peer.audio_stream_out._rate,
                    channels=CHANNELS,
                )

                # Play audio
                await asyncio.to_thread(self.peer.audio_stream_out.write, pcm_data.data)

        except Exception as e:
            logger.error(f'Error playing local audio for peer {self.peer_id}: {e}')

    async def _send_to_gemini(self, msg: SendToGeminiType) -> None:
        """Send message to Gemini session."""
        if not self.gemini_session:
            logger.error(f'[Gemini] No available session for peer {self.peer_id}')
            return

        try:
            if isinstance(msg, types.Blob):
                logger.debug(f'[Gemini] Sending audio to Gemini for peer {self.peer_id}')
                await self.gemini_session.send_realtime_input(audio=msg)
            elif isinstance(msg, types.Content):
                await self.gemini_session.send_client_content(turns=[msg])
            else:
                logger.error(f'[Gemini] Invalid message type: {type(msg)}')
        except Exception as e:
            logger.error(f'Error sending audio to Gemini for peer {self.peer_id}: {e}')

    async def handle_transcript(self, transcript: str) -> None:
        """Handle transcript from Gemini."""
        if not self._data_channel_ready.is_set():
            logger.info(
                f'[LocalAudioLoop] Data channel not ready, queueing transcript '
                f'for peer {self.peer_id}: {transcript}'
            )
            self._pending_transcripts.append(transcript)
            return

        # Emit transcript event
        await self.event_manager.emit_data_channel_event(
            LocalDataChannelEventType.TRANSCRIPT_SENT,
            {'transcript': transcript, 'length': len(transcript)},
        )

        if self.on_transcript_callback:
            await self.on_transcript_callback(transcript, self.peer_id)

    async def _receive_audio_from_gemini(self) -> None:
        """Receive audio from Gemini."""
        try:
            while True:
                input_transcription = []
                output_transcription = []

                try:
                    if not self.gemini_session:
                        logger.error(f'[Gemini] No available session for peer {self.peer_id}')
                        break

                    turn = self.gemini_session.receive()
                    async for response in turn:
                        # Handle audio data
                        if data := response.data:
                            logger.debug(
                                f'[Gemini] Received audio data from Gemini for peer {self.peer_id}'
                            )
                            if self.audio_in_queue:
                                self.audio_in_queue.put_nowait(
                                    types.Blob(data=data, mime_type='audio/pcm')
                                )
                            continue

                        # Handle transcript text
                        if text := response.text:
                            print(text, end='')
                            logger.info(
                                f'[Gemini] Received transcript text from Gemini '
                                f'for peer {self.peer_id}: {text}'
                            )

                        # Handle input transcript
                        if response.server_content.input_transcription:
                            input_transcription.append(
                                response.server_content.input_transcription.text
                            )

                        # Handle output transcript
                        if response.server_content.output_transcription:
                            output_transcription.append(
                                response.server_content.output_transcription.text
                            )

                        # Handle interruption
                        if response.server_content.interrupted is True:
                            logger.info(f'Response interrupted for peer {self.peer_id}')
                            # Clear audio queue
                            if self.audio_in_queue:
                                while not self.audio_in_queue.empty():
                                    try:
                                        self.audio_in_queue.get_nowait()
                                    except asyncio.QueueEmpty:
                                        break

                    # Record transcript results
                    if input_transcription:
                        logger.info(
                            f'[Gemini] Input transcript for peer {self.peer_id}: '
                            f'{"".join(input_transcription)}'
                        )
                    if output_transcription:
                        logger.info(
                            f'[Gemini] Output transcript for peer {self.peer_id}: '
                            f'{"".join(output_transcription)}'
                        )
                        await self.handle_transcript(''.join(output_transcription))

                    logger.debug(f'[Gemini] Completed one turn for peer {self.peer_id}')

                except Exception as turn_error:
                    # Check if it's a normal close
                    if 'sent 1000' in str(turn_error) or 'received 1000' in str(turn_error):
                        logger.info(
                            f'[Gemini] Session closed normally (1000) '
                            f'for peer {self.peer_id}, stopping receive loop'
                        )
                        break
                    else:
                        logger.error(f'Error handling turn for peer {self.peer_id}: {turn_error}')
                        raise

            logger.info(f'[Gemini] Completed receiving audio from Gemini for peer {self.peer_id}')

        except Exception as e:
            logger.error(f'Error receiving audio from Gemini for peer {self.peer_id}: {e}')
            if 'sent 1000' in str(e) or 'received 1000' in str(e):
                logger.warning(
                    f'[Gemini] WebSocket connection closed normally (1000) for peer {self.peer_id}'
                )
            else:
                raise


class LocalWebRTCSimulator:
    """Local WebRTC simulator."""

    def __init__(self) -> None:
        self.peers: dict[str, LocalPeer] = {}

    async def _handle_audio_event(self, event: LocalAudioEvent) -> None:
        """Handle audio events"""
        logger.info(f'[EventHandler] Audio Event: {event.type.value} for peer {event.peer_id}')
        if event.data:
            logger.debug(f'[EventHandler] Audio Event Data: {event.data}')

    async def _handle_session_event(self, event: LocalSessionEvent) -> None:
        """Handle session events"""
        logger.info(f'[EventHandler] Session Event: {event.type.value} for peer {event.peer_id}')
        if event.data:
            logger.debug(f'[EventHandler] Session Event Data: {event.data}')

    async def _handle_data_channel_event(self, event: LocalDataChannelEvent) -> None:
        """Handle data channel events"""
        logger.info(
            f'[EventHandler] Data Channel Event: {event.type.value} for peer {event.peer_id}'
        )
        if event.data:
            logger.debug(f'[EventHandler] Data Channel Event Data: {event.data}')

    async def create_peer(self, peer_id: str) -> LocalPeer:
        """Create a new local Peer."""
        if peer_id in self.peers:
            logger.info(f'Peer {peer_id} already exists, closing old connection')
            await self.peers[peer_id].cleanup()
            del self.peers[peer_id]

        peer = LocalPeer(peer_id=peer_id)
        self.peers[peer_id] = peer
        logger.info(f'Local Peer created successfully for peer {peer_id}')
        return peer

    async def close_peer(self, peer_id: str) -> None:
        """Close Peer connection."""
        if peer_id in self.peers:
            await self.peers[peer_id].cleanup()
            del self.peers[peer_id]
            logger.info(f'Local Peer closed for peer {peer_id}')

    def get_peer(self, peer_id: str) -> LocalPeer | None:
        """Get the specified Peer."""
        return self.peers.get(peer_id)

    async def _handle_transcript(self, transcript: str, peer_id: str) -> None:
        """Handle transcript, simulate sending to data channel."""
        try:
            # Simulate data channel sending
            # message = json.dumps({'transcript': transcript})
            logger.info(
                f'[Simulated data channel] Sending transcript to peer {peer_id}: {transcript}'
            )
            print(f'\n[Transcript] {transcript}')
        except Exception as e:
            logger.error(f'Error sending transcript for peer {peer_id}: {e}')

    async def start_audio_session(self, peer_id: str) -> None:
        """Start audio session."""
        peer = self.get_peer(peer_id)
        if not peer:
            raise ValueError(f'Peer {peer_id} does not exist')

        # Create audio loop
        audio_loop = LocalAudioLoop(peer_id)
        peer.audio_loop = audio_loop

        # Set event handlers
        audio_loop.add_audio_event_handler(self._handle_audio_event)
        audio_loop.add_session_event_handler(self._handle_session_event)
        audio_loop.add_data_channel_event_handler(self._handle_data_channel_event)

        # Set transcript callback
        audio_loop.set_transcript_callback(self._handle_transcript)

        # Mark data channel ready
        audio_loop.mark_data_channel_ready()

        # Start audio loop
        await audio_loop.start(peer)
        logger.info(f'Audio session started successfully for peer {peer_id}')


class InteractiveLoop:
    """Interactive loop, handle user input."""

    def __init__(self, simulator: LocalWebRTCSimulator) -> None:
        self.simulator = simulator

    async def run(self) -> None:
        """Run interactive session."""
        peer_id = 'local_user'

        try:
            # Create Peer
            await self.simulator.create_peer(peer_id)

            # Start audio session
            await self.simulator.start_audio_session(peer_id)

            print('Local WebRTC simulator started successfully!')
            print('Now you can start voice conversation...')
            print("Enter 'q' to exit the program")

            # Wait for user input
            while True:
                text = await asyncio.to_thread(input, 'message > ')
                if text.lower() == 'q':
                    break

                # Handle text input (if needed)
                logger.info(f'User input: {text}')

        except KeyboardInterrupt:
            print('\nProgram interrupted by user')
        except Exception as e:
            logger.error(f'Error: {e}', exc_info=True)
        finally:
            # Clean up resources
            await self.simulator.close_peer(peer_id)
            print('Program exited')


async def main() -> None:
    """Main function."""
    try:
        simulator = LocalWebRTCSimulator()
        interactive_loop = InteractiveLoop(simulator)
        await interactive_loop.run()
    except Exception as e:
        logger.error(f'Main program error: {e}', exc_info=True)
    finally:
        # Clean up PyAudio
        pya.terminate()


if __name__ == '__main__':
    asyncio.run(main())
