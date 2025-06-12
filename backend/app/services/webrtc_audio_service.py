"""
WebRTC Audio Service

Handles audio processing, voice activity detection, transcription,
and communication with Gemini for WebRTC connections.
"""

import asyncio
import contextlib
import logging
import time
from typing import TYPE_CHECKING, Optional, Union

import av
import numpy as np
from aiortc import MediaStreamTrack
from google import genai
from google.genai import types
from google.genai.live import AsyncSession

from app.connections.gemini_client import LIVE_CONFIG, MODEL, get_client
from app.schemas.webrtc_schema import WebRTCDataChannelMessage
from app.services.audio_processor import (
    OPUS_SAMPLE_RATE,
    RECEIVE_SAMPLE_RATE,
    SEND_SAMPLE_RATE,
    AudioChunkSegmenter,
    AudioStreamTrack,
    resample_pcm_audio,
    save_pcm_audio_to_wav,
)
from app.services.webrtc_event_manager import webrtc_event_manager
from app.services.webrtc_events import (
    WebRTCAudioEvent,
    WebRTCAudioEventType,
    WebRTCDataChannelEventType,
    WebRTCSessionEventType,
)

if TYPE_CHECKING:
    from app.services.webrtc_service import Peer

logger = logging.getLogger(__name__)


class WebRTCAudioLoop:
    """
    Audio processing loop for WebRTC connections.

    Handles:
    - Audio stream processing
    - Voice activity detection
    - Transcription
    - Communication with Gemini
    - Event emission for business logic
    """

    def __init__(self, peer_id: str) -> None:
        self.peer_id = peer_id
        self.gemini_session: genai.ChatSession | None = None
        self._pending_transcripts: list[WebRTCDataChannelMessage] = []
        self._is_voice_active = False
        self._task_group: asyncio.TaskGroup | None = None

        # Audio queues
        self.audio_in_queue: asyncio.Queue[bytes] | None = (
            None  # Audio FROM Gemini (for playback to user)
        )
        self.audio_out_queue: asyncio.Queue[types.Blob] | None = (
            None  # Audio TO Gemini (from user input)
        )

        # Get event manager for this peer
        self.event_manager = webrtc_event_manager.get_or_create_peer_manager(peer_id)

        # WebRTC-specific attributes (will be set in start method)
        self.webrtc_track = None
        self.peer = None
        self.server_audio_track = None

        # Gemini session management
        self.gemini_client = get_client()
        self.gemini_session = None

        # Voice activity detection
        self.last_voice_time = time.time()
        self.silence_timeout = 1.0
        self._is_voice_active = False

        # Add debounce for AUDIO_STREAM_END events to prevent spam
        self._last_audio_stream_end_time = 0
        self._audio_stream_end_debounce = 2.0  # Prevent rapid AUDIO_STREAM_END events

        # Add turn completion logic
        self._user_has_spoken = False  # Track if user has spoken since last response
        self._last_turn_complete_time = 0
        self._turn_complete_debounce = 5.0  # Minimum time between turn complete signals

        # Add Gemini speaking state to prevent audio feedback
        self._gemini_is_speaking = False
        self._gemini_last_audio_time = 0
        self._gemini_speaking_timeout = 2.0  # Consider Gemini stopped speaking after 2s of no audio

        # Task management
        self._main_task = None

        self.segmenter = AudioChunkSegmenter()

        logger.info(f'[WebRTCAudioLoop] Created for peer {peer_id}')

    async def start(
        self,
        webrtc_track: MediaStreamTrack | None = None,
        peer: Optional['Peer'] = None,
        server_audio_track: AudioStreamTrack | None = None,
    ) -> None:
        """Start the audio processing loop"""
        logger.info(f'[WebRTCAudioLoop] Starting audio loop for peer {self.peer_id}')

        # Store WebRTC-specific objects if provided
        if webrtc_track:
            self.webrtc_track = webrtc_track
        if peer:
            self.peer = peer
        if server_audio_track:
            self.server_audio_track = server_audio_track

        # Initialize queues
        self.audio_in_queue = asyncio.Queue()
        self.audio_out_queue = asyncio.Queue(maxsize=5)

        # Start main task
        self._main_task = asyncio.create_task(self._audio_processing_loop())

        logger.info(f'WebRTC Audio Loop with Gemini session started for peer {self.peer_id}')

    async def stop(self) -> None:
        """Stop the audio processing loop"""
        logger.info(f'[WebRTCAudioLoop] Stopping audio loop for peer {self.peer_id}')

        # Emit session ending event
        await self.event_manager.emit_session_event(
            WebRTCSessionEventType.SESSION_ENDED, {'message': 'WebRTC audio session ending'}
        )

        # Emit audio stream end event
        await self.event_manager.emit_audio_event(
            WebRTCAudioEventType.AUDIO_STREAM_END, {'message': 'Audio stream stopped'}
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

        logger.info(f'WebRTC Audio Loop stopped for peer {self.peer_id}')

    async def _send_pending_transcripts(self) -> None:
        """Send all pending transcripts through events"""
        if not self._pending_transcripts:
            return

        logger.info(
            f'[WebRTCAudioLoop] Processing {len(self._pending_transcripts)} '
            f'pending transcripts for peer {self.peer_id}'
        )

        for transcript in self._pending_transcripts:
            try:
                await self.event_manager.emit_data_channel_event(
                    WebRTCDataChannelEventType.TRANSCRIPT_SENT, transcript
                )
            except Exception as e:
                logger.error(
                    f'[WebRTCAudioLoop] Error sending pending transcript '
                    f'for peer {self.peer_id}: {e}'
                )

        # Clear pending transcripts
        self._pending_transcripts.clear()
        logger.info(f'[WebRTCAudioLoop] All pending transcripts sent for peer {self.peer_id}')

    def set_gemini_session(self, session: AsyncSession) -> None:
        """Set the Gemini session for this audio loop"""
        self.gemini_session = session
        logger.info(f'[WebRTCAudioLoop] Gemini session set for peer {self.peer_id}')

    async def add_audio_data(self, audio_data: bytes) -> None:
        """Add audio data from Gemini to the playback queue"""
        if self.audio_in_queue:
            await self.audio_in_queue.put(audio_data)

    async def _audio_processing_loop(self) -> None:
        """Main audio processing loop - integrates with Gemini"""
        logger.info(f'[WebRTCAudioLoop] Audio processing loop started for peer {self.peer_id}')

        # Emit audio stream start event
        await self.event_manager.emit_audio_event(WebRTCAudioEventType.AUDIO_STREAM_START)

        try:
            # Use proper context management like live_agent_stream.py
            async with (
                self.gemini_client.aio.live.connect(model=MODEL, config=LIVE_CONFIG) as session,
                asyncio.TaskGroup() as tg,
            ):
                self.gemini_session = session
                logger.info(f'[Gemini] Session started for peer {self.peer_id}')

                # Emit Gemini connected event
                await self.event_manager.emit_session_event(
                    WebRTCSessionEventType.GEMINI_CONNECTED,
                    {'message': 'Connected to Gemini Live API'},
                )

                # DO NOT send any initial message to Gemini - wait for user to speak first
                logger.info(
                    f'[Gemini] Waiting for user input before starting conversation '
                    f'for peer {self.peer_id}'
                )

                # Start all tasks within the TaskGroup
                tg.create_task(self._listen_webrtc_audio())
                tg.create_task(self._send_realtime())
                tg.create_task(self._play_webrtc_audio())
                tg.create_task(self._receive_audio_from_gemini())

                # This will keep the session alive until cancelled or an error occurs
                await asyncio.sleep(float('inf'))

        except asyncio.CancelledError:
            logger.info(f'[Gemini] Session cancelled for peer {self.peer_id}')
            await self.event_manager.emit_session_event(
                WebRTCSessionEventType.GEMINI_DISCONNECTED,
                {'message': 'Gemini session cancelled by user'},
            )
        except Exception as e:
            logger.error(f'[Gemini] Session error for peer {self.peer_id}: {e}', exc_info=True)
            await self.event_manager.emit_session_event(
                WebRTCSessionEventType.SESSION_ERROR,
                {'error': str(e), 'message': 'Gemini session error'},
            )
        finally:
            self.gemini_session = None
            logger.info(f'[Gemini] Session ended for peer {self.peer_id}')
            await self.event_manager.emit_session_event(
                WebRTCSessionEventType.GEMINI_DISCONNECTED, {'message': 'Gemini session ended'}
            )

    async def _listen_webrtc_audio(self) -> None:
        """Listen to WebRTC audio and emit events"""
        while True:
            if not self.webrtc_track:
                await asyncio.sleep(0.1)
                continue

            frame = await self.webrtc_track.recv()
            audio_array = frame.to_ndarray()
            audio_bytes = audio_array.tobytes()

            # Resample to Gemini required sample rate first (before silence detection)
            if frame.rate != SEND_SAMPLE_RATE:
                logger.debug(
                    f'[WebRTC] Resampling audio for peer {self.peer_id} '
                    f'from {frame.rate} to {SEND_SAMPLE_RATE}'
                )
                try:
                    audio_bytes = resample_pcm_audio(audio_bytes, frame.rate)
                    logger.debug(
                        f'[WebRTC] Audio resampled successfully, new length: {len(audio_bytes)}'
                    )
                except Exception as e:
                    logger.error(f'[WebRTC] Failed to resample audio for peer {self.peer_id}: {e}')
                    continue

            # Check if Gemini is currently speaking and skip processing to prevent feedback
            current_time = time.time()
            if self._gemini_is_speaking:
                # Check if Gemini has stopped speaking (timeout)
                if current_time - self._gemini_last_audio_time > self._gemini_speaking_timeout:
                    self._gemini_is_speaking = False
                    logger.debug(
                        f'[WebRTC] Gemini speaking timeout, '
                        f'resuming user audio processing for peer {self.peer_id}'
                    )
                else:
                    # Skip processing while Gemini is speaking
                    logger.debug(
                        f'[WebRTC] Skipping user audio processing while Gemini is speaking '
                        f'for peer {self.peer_id}'
                    )
                    continue

            # Segment audio chunks into meaningful utterances for Gemini
            segments = self.segmenter.feed(audio_bytes)
            for seg in segments:
                # Only process meaningful speech segments
                if seg and len(seg) > 0:
                    # Voice activity detected
                    if not self._is_voice_active:
                        self._is_voice_active = True
                        self._user_has_spoken = True  # Mark that user has spoken
                        await self.event_manager.emit_audio_event(
                            WebRTCAudioEventType.VOICE_ACTIVITY_DETECTED,
                            {'message': 'Voice activity started', 'audio_length': len(seg)},
                        )
                    self.last_voice_time = time.time()
                    if self.audio_out_queue:
                        logger.info(
                            f'[WebRTC] SENDING USER AUDIO to Gemini for peer {self.peer_id}, '
                            f'length: {len(seg)}'
                        )
                        await self.event_manager.emit_audio_event(
                            WebRTCAudioEventType.AUDIO_CHUNK_READY,
                            {
                                'message': 'Audio chunk ready',
                                'audio_data': seg,
                                'timestamp': time.time(),
                            },
                        )
                        await self.audio_out_queue.put(types.Blob(data=seg, mime_type='audio/pcm'))

            # Check for silence (if current frame is silent and was previously active,
            # trigger silence event)
            if not segments and not self.segmenter.last_voice_time and self._is_voice_active:
                self._is_voice_active = False
                await self.event_manager.emit_audio_event(
                    WebRTCAudioEventType.SILENCE_DETECTED,
                    {
                        'message': 'Voice activity stopped',
                        'duration': time.time() - self.last_voice_time,
                    },
                )

            # Check if AUDIO_STREAM_END event should be triggered
            if (
                self.gemini_session
                and time.time() - self.last_voice_time > self.silence_timeout
                and time.time() - self._last_audio_stream_end_time > self._audio_stream_end_debounce
            ):
                await self.event_manager.emit_audio_event(
                    WebRTCAudioEventType.AUDIO_STREAM_END,
                    {'message': 'Audio stream ended'},
                )
                self.last_voice_time = time.time()
                self._last_audio_stream_end_time = time.time()

    async def _send_realtime(self) -> None:
        """Send audio to Gemini, prioritizing events."""
        try:
            while self.audio_out_queue:
                audio_msg = await self.audio_out_queue.get()
                await self._send_to_gemini_session(audio_msg)
                logger.debug(f'[WebRTC] Audio sent to Gemini for peer {self.peer_id}')
        except Exception as e:
            logger.error(f'Error in sending audio to Gemini for peer {self.peer_id}: {e}')

    async def _play_webrtc_audio(self) -> None:
        """Play audio to WebRTC by pushing frames to the streaming track."""
        try:
            # WebRTC Opus encoders work best with 20ms frames
            frame_duration_ms = 20
            samples_per_frame = int(OPUS_SAMPLE_RATE * frame_duration_ms / 1000)
            # 16-bit PCM has 2 bytes per sample
            bytes_per_frame = samples_per_frame * 2
            timestamp = 0

            while self.audio_in_queue and self.server_audio_track:
                # Get PCM data from queue (from Gemini)
                pcm_data = await self.audio_in_queue.get()

                # Resample from Gemini's output rate to the track's rate
                resampled_pcm = resample_pcm_audio(
                    pcm_data.data, RECEIVE_SAMPLE_RATE, OPUS_SAMPLE_RATE
                )

                # Chunk the resampled data into 20ms frames
                for i in range(0, len(resampled_pcm), bytes_per_frame):
                    chunk = resampled_pcm[i : i + bytes_per_frame]
                    if len(chunk) < bytes_per_frame:
                        continue  # Drop incomplete frame

                    # Create AudioFrame for aiortc
                    frame = av.AudioFrame.from_ndarray(
                        np.frombuffer(chunk, dtype=np.int16).reshape(1, -1),
                        format='s16',
                        layout='mono',
                    )
                    frame.sample_rate = OPUS_SAMPLE_RATE
                    # Timestamps are crucial for smooth playback
                    frame.pts = timestamp
                    timestamp += samples_per_frame

                    await self.server_audio_track.add_frame(frame)

        except Exception as e:
            logger.error(
                f'Error in playing WebRTC audio for peer {self.peer_id}: {e}', exc_info=True
            )
        finally:
            if self.server_audio_track:
                # Signal the track to stop
                await self.server_audio_track.add_frame(None)

    async def _send_to_gemini_session(self, msg: Union[types.Blob, str, types.Content]) -> None:
        """Send message to Gemini session"""
        if not self.gemini_session:
            logger.error(f'[Gemini] No session available for peer {self.peer_id}')
            return

        try:
            if isinstance(msg, types.Blob):
                logger.info(
                    f'[Gemini] SENDING AUDIO to Gemini for peer {self.peer_id}, '
                    f'length: {len(msg.data)} bytes'
                )
                await self.gemini_session.send_realtime_input(audio=msg)
            elif isinstance(msg, types.Content):
                await self.gemini_session.send_client_content(
                    turns=[
                        msg,
                    ]
                )
            else:
                logger.error(f'[Gemini] Invalid message type: {type(msg)}')
        except Exception as e:
            logger.error(f'Error sending audio to Gemini for peer {self.peer_id}: {e}')

    async def _receive_audio_from_gemini(self) -> None:
        """Receive and process audio from Gemini"""
        try:
            # Process turns from the session in a loop (like original live_agent_stream.py)
            while True:
                input_transcription = []
                output_transcription = []

                try:
                    if not self.gemini_session:
                        logger.error(f'[Gemini] No session available for peer {self.peer_id}')
                        break

                    turn = self.gemini_session.receive()
                    async for response in turn:
                        # Handle audio data
                        logger.debug(
                            f'[Gemini] Received response from Gemini for peer {self.peer_id}'
                        )
                        if data := response.data:
                            # Mark that Gemini is speaking
                            self._gemini_is_speaking = True
                            self._gemini_last_audio_time = time.time()

                            # Put audio data directly into the queue (sync, like working version)
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

                        # Handle input transcription
                        if response.server_content.input_transcription:
                            input_text = response.server_content.input_transcription.text
                            input_transcription.append(input_text)
                            logger.info(
                                f'[Gemini] RECEIVED INPUT TRANSCRIPTION: "{input_text}" '
                                f'for peer {self.peer_id}'
                            )

                        # Handle output transcription
                        if response.server_content.output_transcription:
                            output_transcription.append(
                                response.server_content.output_transcription.text
                            )

                        # Handle interruption, inspired by AudioLoop interruption logic
                        if response.server_content.interrupted is True:
                            logger.info(f'Response interrupted for peer {self.peer_id}')
                            # Clear audio queue
                            if self.audio_in_queue:
                                while not self.audio_in_queue.empty():
                                    try:
                                        self.audio_in_queue.get_nowait()
                                    except asyncio.QueueEmpty:
                                        break

                    # Log transcription results at the end of each turn
                    if input_transcription:
                        logger.info(
                            f'[Gemini] Input transcript for peer {self.peer_id}: '
                            f'{"".join(input_transcription)}'
                        )
                        # Fire a transcript event instead of calling handle_transcript
                        transcript = ''.join(input_transcription)
                        await self.event_manager.emit_data_channel_event(
                            WebRTCDataChannelEventType.TRANSCRIPT_SENT,
                            {'transcript': WebRTCDataChannelMessage(role='user', text=transcript)},
                        )
                    if output_transcription:
                        logger.info(
                            f'[Gemini] Output transcript for peer {self.peer_id}: '
                            f'{"".join(output_transcription)}'
                        )
                        # Fire a transcript event instead of calling handle_transcript
                        transcript = ''.join(output_transcription)
                        await self.event_manager.emit_data_channel_event(
                            WebRTCDataChannelEventType.TRANSCRIPT_SENT,
                            {
                                'transcript': WebRTCDataChannelMessage(
                                    role='assistant', text=transcript
                                )
                            },
                        )

                    logger.info(f'[Gemini] Finished one turn for peer {self.peer_id}')
                    # Reset user spoken flag when Gemini finishes responding
                    self._user_has_spoken = False
                    # Reset Gemini speaking flag when turn is complete
                    self._gemini_is_speaking = False

                except Exception as turn_error:
                    # Check if this is a connection closed error
                    if 'sent 1000' in str(turn_error) or 'received 1000' in str(turn_error):
                        logger.info(
                            f'[Gemini] Session closed normally (1000) '
                            f'for peer {self.peer_id}, stopping receive loop'
                        )
                        break  # Exit the while loop gracefully
                    else:
                        # For other errors, re-raise
                        logger.error(f'Error processing turn for peer {self.peer_id}: {turn_error}')
                        raise

            logger.info(f'[Gemini] Finished receiving audio from Gemini for peer {self.peer_id}')

        except Exception as e:
            logger.error(f'Error receiving audio from Gemini for peer {self.peer_id}: {e}')
            # Check if this is a connection closed error
            if 'sent 1000' in str(e) or 'received 1000' in str(e):
                logger.warning(
                    f'[Gemini] WebSocket connection was closed normally (1000) '
                    f'for peer {self.peer_id}'
                )
            else:
                # For other errors, we might want to re-raise
                raise


class WebRTCAudioService:
    """Service for managing WebRTC audio processing"""

    def __init__(self) -> None:
        self.audio_loops: dict[str, WebRTCAudioLoop] = {}

    def create_audio_loop(self, peer_id: str) -> WebRTCAudioLoop:
        """
        Create and register an audio loop for a peer,
        and register AUDIO_STREAM_END event hook
        """
        if peer_id in self.audio_loops:
            logger.warning(f'[WebRTCAudioService] Audio loop already exists for peer {peer_id}')
            return self.audio_loops[peer_id]

        audio_loop = WebRTCAudioLoop(peer_id)
        self.audio_loops[peer_id] = audio_loop
        logger.info(f'[WebRTCAudioService] Created audio loop for peer {peer_id}')

        event_manager = audio_loop.event_manager

        # Add a new event handler for audio stream start
        @event_manager.on_audio_event(WebRTCAudioEventType.AUDIO_STREAM_START)
        async def on_audio_stream_start(event: WebRTCAudioEvent) -> None:
            logger.info(f'[WebRTCAudioService] Audio stream started for peer {peer_id}')

        @event_manager.on_audio_event(WebRTCAudioEventType.AUDIO_CHUNK_READY)
        async def on_audio_chunk_ready(event: WebRTCAudioEvent) -> None:
            logger.info(f'[WebRTCAudioService] Audio chunk ready for peer {peer_id}')
            chunk_data = event.data.get('audio_data', None)
            timestamp = event.data.get('timestamp', None)
            if chunk_data and timestamp:
                file_path = f'peer_{event.peer_id}_chunk_{int(timestamp * 1000)}.wav'
                save_pcm_audio_to_wav(chunk_data, file_path)
                logger.info(f'[WebRTCAudioService] Saved audio chunk to {file_path}')

        # Smart AUDIO_STREAM_END event handler that only sends turn_complete when appropriate
        @event_manager.on_audio_event(WebRTCAudioEventType.AUDIO_STREAM_END)
        async def on_audio_stream_end(event: WebRTCAudioEvent) -> None:
            current_time = time.time()

            # Only send turn_complete if:
            # 1. User has actually spoken since last response
            # 2. Enough time has passed since last turn_complete signal
            # 3. Gemini session exists
            if (
                audio_loop.gemini_session
                and audio_loop._user_has_spoken
                and current_time - audio_loop._last_turn_complete_time
                > audio_loop._turn_complete_debounce
            ):
                try:
                    await audio_loop.gemini_session.send_client_content(
                        turns=[types.Content(role='user', parts=[types.Part(text='')])],
                        turn_complete=True,
                    )
                    audio_loop._user_has_spoken = False  # Reset flag
                    audio_loop._last_turn_complete_time = current_time  # Update debounce time
                    logger.info(f'[Gemini] Sent turn_complete signal for peer {audio_loop.peer_id}')
                except Exception as e:
                    logger.error(
                        f'[Gemini] Error sending turn_complete for peer {audio_loop.peer_id}: {e}'
                    )

        return audio_loop

    def get_audio_loop(self, peer_id: str) -> WebRTCAudioLoop | None:
        """Get audio loop for a peer"""
        return self.audio_loops.get(peer_id)

    async def remove_audio_loop(self, peer_id: str) -> None:
        """Remove and cleanup audio loop for a peer"""
        if peer_id in self.audio_loops:
            audio_loop = self.audio_loops[peer_id]
            try:
                await audio_loop.stop()
            except Exception as e:
                logger.error(
                    f'[WebRTCAudioService] Error stopping audio loop for peer {peer_id}: {e}'
                )

            del self.audio_loops[peer_id]
            logger.info(f'[WebRTCAudioService] Removed audio loop for peer {peer_id}')

    def get_all_peer_ids(self) -> list[str]:
        """Get all active peer IDs with audio loops"""
        return list(self.audio_loops.keys())


# Global audio service instance
webrtc_audio_service = WebRTCAudioService()


def get_webrtc_audio_service() -> WebRTCAudioService:
    """Get the global WebRTC audio service instance"""
    return webrtc_audio_service
