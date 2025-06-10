from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Union

import av
import numpy as np
from aiortc import (
    RTCConfiguration,
    RTCDataChannel,
    RTCIceServer,
    RTCPeerConnection,
    RTCRtpTransceiver,
)
from aiortc.mediastreams import MediaStreamTrack
from google import genai
from google.genai import types
from google.genai.live import AsyncSession

from app.connections.gemini_client import LIVE_CONFIG, MODEL, get_client
from app.schemas.webrtc_schema import (
    WebRTCAudioEvent,
    WebRTCAudioEventType,
    WebRTCDataChannelError,
    WebRTCMediaError,
    WebRTCPeerError,
)
from app.services.audio_processor import (
    OPUS_SAMPLE_RATE,
    RECEIVE_SAMPLE_RATE,
    SEND_SAMPLE_RATE,
    AudioStreamTrack,
    is_silence,
    resample_pcm_audio,
)

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

RTC_CONFIG = RTCConfiguration(
    iceServers=[
        RTCIceServer(
            urls=[
                'stun:stun.l.google.com:19302',
            ]
        ),
    ]
)

# Callback type definitions
SendToGeminiType = Union[types.Blob, WebRTCAudioEvent]
SendToGeminiCallback = Callable[[SendToGeminiType], Awaitable[None]]

# Transcript callback: (transcript, peer_id) -> None
TranscriptCallback = Callable[[str, str], Awaitable[None]]

# Audio track callback: (track, peer_id) -> None
AudioTrackCallback = Callable[[MediaStreamTrack, str], Awaitable[None]]

# Data channel callback: (channel, peer_id) -> None
DataChannelCallback = Callable[[RTCDataChannel, str], Awaitable[None]]


@dataclass
class Peer:
    """Peer connection and its associated resources"""

    peer_id: str
    connection: RTCPeerConnection
    transceiver: RTCRtpTransceiver | None = None
    data_channel: RTCDataChannel | None = None
    audio_loop: WebRTCAudioLoop | None = None  # Forward reference

    async def cleanup(self) -> None:
        """Cleanup all resources associated with this peer"""
        # Clean up audio loop first
        if self.audio_loop:
            await self.audio_loop.stop()
        # Clean up transceiver
        if self.transceiver:
            self.transceiver.stop()
        # Clean up data channel
        if self.data_channel:
            self.data_channel.close()
        # Close peer connection
        await self.connection.close()


class PeerSessionManager:
    """Manage the lifecycle of WebRTC Peer connections"""

    def __init__(self) -> None:
        self.peers: dict[str, Peer] = {}
        self.on_track_callback: AudioTrackCallback | None = None
        self.on_datachannel_callback: DataChannelCallback | None = None

    def set_track_callback(self, callback: AudioTrackCallback) -> None:
        """Set callback for track events"""
        self.on_track_callback = callback

    def set_datachannel_callback(self, callback: DataChannelCallback) -> None:
        """Set callback for data channel events"""
        self.on_datachannel_callback = callback

    async def create_peer(self, peer_id: str) -> Peer:
        """Create a new Peer connection"""
        if peer_id in self.peers:
            logger.debug(f'Peer {peer_id} already exists, closing old connection')
            await self.peers[peer_id].cleanup()
            del self.peers[peer_id]

        # Create peer connection
        pc = RTCPeerConnection(RTC_CONFIG)

        # Add transceiver for audio
        try:
            transceiver = pc.addTransceiver('audio', direction='sendrecv')
            logger.debug(f'Created transceiver for peer {peer_id}')
        except Exception as e:
            raise WebRTCMediaError(f'Failed to create audio transceiver: {str(e)}', peer_id) from e

        @pc.on('datachannel')
        async def on_datachannel(channel: RTCDataChannel) -> None:
            if self.on_datachannel_callback:
                await self.on_datachannel_callback(channel, peer_id)

        @pc.on('track')
        async def on_track(track: MediaStreamTrack) -> None:
            if self.on_track_callback:
                await self.on_track_callback(track, peer_id)

        peer = Peer(connection=pc, peer_id=peer_id, transceiver=transceiver)
        self.peers[peer_id] = peer
        logger.info(f'Peer connection created for peer {peer_id}')
        return peer

    async def close_peer(self, peer_id: str) -> None:
        """Close a Peer connection"""
        try:
            if peer_id in self.peers:
                await self.peers[peer_id].cleanup()
                del self.peers[peer_id]
                logger.info(f'Peer connection closed for peer {peer_id}')
        except Exception as e:
            raise WebRTCPeerError(f'Error closing peer connection: {str(e)}', peer_id) from e

    def get_peer(self, peer_id: str) -> Peer | None:
        """Get the specified Peer"""
        return self.peers.get(peer_id)


class WebRTCAudioLoop:
    """WebRTC audio stream processor integrating AudioLoop capabilities"""

    def __init__(self, peer_id: str) -> None:
        self.peer_id = peer_id
        # Queues for audio in/out, inspired by AudioLoop
        self.audio_in_queue: asyncio.Queue[types.Blob] | None = None  # Audio received from Gemini
        self.audio_out_queue: asyncio.Queue[types.Blob] | None = None  # Audio to send to Gemini
        self.event_queue: asyncio.Queue | None = None  # Control events (e.g., audio_stream_end)

        # TaskGroup for managing tasks
        self._tg: asyncio.TaskGroup | None = None
        self._main_task: asyncio.Task | None = None

        # WebRTC specific attributes
        self.webrtc_track: MediaStreamTrack | None = None
        self.peer: Peer | None = None
        self.server_audio_track: AudioStreamTrack | None = None

        # Gemini session management - integrated directly
        self.gemini_client: genai.Client = get_client()
        self.gemini_session: AsyncSession | None = None

        # Callback for transcript handling
        self.on_transcript_callback: TranscriptCallback | None = None

        self.last_voice_time = time.time()
        self.silence_timeout = 1.0

    def set_transcript_callback(self, callback: TranscriptCallback) -> None:
        """Set callback for transcript handling"""
        self.on_transcript_callback = callback

    async def start(
        self, webrtc_track: MediaStreamTrack, peer: Peer, server_audio_track: AudioStreamTrack
    ) -> None:
        """Start audio stream processing with integrated Gemini session, use TaskGroup"""

        self.webrtc_track = webrtc_track
        self.peer = peer
        self.server_audio_track = server_audio_track

        # Initialize queues
        self.audio_in_queue = asyncio.Queue[types.Blob]()
        self.audio_out_queue = asyncio.Queue[types.Blob](maxsize=5)
        self.event_queue = asyncio.Queue[WebRTCAudioEvent]()

        self._main_task = asyncio.create_task(self._run_with_gemini())

        logger.info(f'WebRTC Audio Loop with Gemini session started for peer {self.peer_id}')

    async def _run_with_gemini(self) -> None:
        """Run audio tasks with integrated Gemini session management"""
        try:
            # Use proper context management like live_agent_stream.py
            async with (
                self.gemini_client.aio.live.connect(model=MODEL, config=LIVE_CONFIG) as session,
                asyncio.TaskGroup() as tg,
            ):
                self.gemini_session = session
                logger.info(f'[Gemini] Session started for peer {self.peer_id}')

                # Start all tasks within the TaskGroup
                tg.create_task(self._listen_webrtc_audio())
                tg.create_task(self._send_realtime())
                tg.create_task(self._play_webrtc_audio())
                tg.create_task(self._receive_audio_from_gemini())

                # This will keep the session alive until cancelled or an error occurs
                await asyncio.sleep(float('inf'))

        except asyncio.CancelledError:
            logger.info(f'[Gemini] Session cancelled for peer {self.peer_id}')
        except Exception as e:
            logger.error(f'[Gemini] Session error for peer {self.peer_id}: {e}', exc_info=True)
        finally:
            self.gemini_session = None
            logger.info(f'[Gemini] Session ended for peer {self.peer_id}')

    async def stop(self) -> None:
        """Stop audio stream processing, TaskGroup cleanup"""

        if self._main_task:
            self._main_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._main_task
            self._main_task = None

        if self.audio_in_queue:
            while not self.audio_in_queue.empty():
                try:
                    self.audio_in_queue.get_nowait()
                except asyncio.QueueEmpty:
                    break

        logger.info(f'WebRTC Audio Loop stopped for peer {self.peer_id}')

    async def _listen_webrtc_audio(self) -> None:
        while True:
            frame = await self.webrtc_track.recv()
            audio_array = frame.to_ndarray()
            audio_bytes = audio_array.tobytes()
            if not audio_bytes or len(audio_bytes) < 320 or is_silence(audio_bytes):
                if (
                    self.gemini_session
                    and time.time() - self.last_voice_time > self.silence_timeout
                ):
                    await self._send_to_gemini(
                        WebRTCAudioEvent(type=WebRTCAudioEventType.AUDIO_STREAM_END)
                    )
                    self.last_voice_time = time.time()  # Reset the last voice time
                continue
            self.last_voice_time = time.time()
            # Resample to Gemini required sample rate
            if frame.rate != SEND_SAMPLE_RATE:
                logger.debug(
                    f'[WebRTC] Resampling audio for peer {self.peer_id} '
                    f'from {frame.rate} to {SEND_SAMPLE_RATE}'
                )
                try:
                    audio_bytes = resample_pcm_audio(audio_bytes, frame.rate, SEND_SAMPLE_RATE)
                    logger.debug(
                        f'[WebRTC] Audio resampled successfully, new length: {len(audio_bytes)}'
                    )
                except Exception as e:
                    logger.error(f'[WebRTC] Failed to resample audio for peer {self.peer_id}: {e}')
                    continue
            if self.audio_out_queue:
                await self.audio_out_queue.put(types.Blob(data=audio_bytes, mime_type='audio/pcm'))

    async def _send_realtime(self) -> None:
        """Send audio to Gemini, prioritizing events."""
        try:
            while self.audio_out_queue:
                audio_msg = await self.audio_out_queue.get()
                await self._send_to_gemini(audio_msg)
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

    async def _send_to_gemini(self, msg: SendToGeminiType) -> None:
        """Callback for sending audio to Gemini session"""
        if not self.gemini_session:
            logger.error(f'[Gemini] No session available for peer {self.peer_id}')
            return

        try:
            if isinstance(msg, WebRTCAudioEvent):
                if msg.type == WebRTCAudioEventType.AUDIO_STREAM_END:
                    await self.gemini_session.send_realtime_input(audio_stream_end=True)
            elif isinstance(msg, types.Blob):
                logger.debug(f'[Gemini] Sending audio to Gemini for peer {self.peer_id}')
                await self.gemini_session.send_realtime_input(
                    audio=msg, activity_end=types.ActivityEnd()
                )
            else:
                logger.error(f'[Gemini] Invalid message type: {type(msg)}')
        except Exception as e:
            logger.error(f'Error sending audio to Gemini for peer {self.peer_id}: {e}')

    async def handle_transcript(self, transcript: str) -> None:
        """Handle transcript text"""
        if self.on_transcript_callback:
            await self.on_transcript_callback(transcript, self.peer_id)

    async def _receive_audio_from_gemini(self) -> None:
        """Receive audio from Gemini, inspired by AudioLoop.receive_audio()"""
        try:
            logger.info(f'[Gemini] Starting to receive audio from Gemini for peer {self.peer_id}')

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
                            logger.info(
                                f'[Gemini] Received audio data from Gemini for peer {self.peer_id}'
                            )
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
                            input_transcription.append(
                                response.server_content.input_transcription.text
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
                            f'Input transcript for peer {self.peer_id}: '
                            f'{"".join(input_transcription)}'
                        )
                    if output_transcription:
                        logger.info(
                            f'Output transcript for peer {self.peer_id}: '
                            f'{"".join(output_transcription)}'
                        )
                        await self.handle_transcript(''.join(output_transcription))

                    logger.info(f'[Gemini] Finished one turn for peer {self.peer_id}')

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


class WebRTCService:
    """Business orchestration layer for WebRTC service"""

    def __init__(self) -> None:
        """Initialize the WebRTC service"""
        self.peer_session_manager = PeerSessionManager()

        # Set callbacks
        self.peer_session_manager.set_track_callback(self._handle_audio_track)
        self.peer_session_manager.set_datachannel_callback(self._handle_data_channel)

    async def _handle_data_channel(self, channel: RTCDataChannel, peer_id: str) -> None:
        """Handle data channel events"""
        try:
            logger.info(f'[DataChannel] Received data channel: {channel.label}')
            logger.debug(f'[DataChannel] Channel state: {channel.readyState}')
            logger.debug(f'[DataChannel] Channel protocol: {channel.protocol}')
            logger.debug(f'[DataChannel] Channel negotiated: {channel.negotiated}')
            logger.debug(f'[DataChannel] Channel id: {channel.id}')

            if channel.label == 'transcript':
                peer = self.peer_session_manager.get_peer(peer_id)
                if peer:
                    peer.data_channel = channel

                @channel.on('open')
                def on_transcript_open() -> None:
                    logger.info(f'Transcript channel opened for peer {peer_id}')

                @channel.on('close')
                def on_transcript_close() -> None:
                    logger.info(f'Transcript channel closed for peer {peer_id}')

                @channel.on('message')
                def on_transcript_message(message: str) -> None:
                    logger.info(f'Received transcript message from peer {peer_id}: {message}')

            logger.debug(f'[DataChannel] Stored received data channel for peer {peer_id}')
        except Exception as e:
            raise WebRTCDataChannelError(f'Error handling data channel: {str(e)}', peer_id) from e

    async def _handle_audio_track(self, track: MediaStreamTrack, peer_id: str) -> None:
        """Handle audio track events"""
        try:
            logger.info(f'Track {track.kind} received for peer {peer_id}')
            if track.kind == 'audio':
                logger.info(
                    f'[WebRTC] Audio track received for peer {peer_id}, '
                    f'setting up WebRTC Audio Loop pipeline'
                )

            # Get peer object
            peer = self.peer_session_manager.get_peer(peer_id)
            if not peer:
                raise WebRTCPeerError(f'Peer {peer_id} not found', peer_id)

            # Create WebRTC Audio Loop
            audio_loop = WebRTCAudioLoop(peer_id)

            # Create and set up the outbound audio track using our streamable version
            server_audio_track = AudioStreamTrack()
            if peer.transceiver and peer.transceiver.sender:
                peer.transceiver.sender.replaceTrack(server_audio_track)
            else:
                raise WebRTCMediaError(f'Cannot find sender for peer {peer_id}', peer_id)

            # Register to Peer object
            peer.audio_loop = audio_loop

            # Set transcript callback
            audio_loop.set_transcript_callback(self._handle_transcript)

            # Start audio loop with the streamable track
            await audio_loop.start(track, peer, server_audio_track)
            logger.info(f'[WebRTC] WebRTCAudioLoop started for peer {peer_id}')

            logger.debug('WebRTC Audio Loop pipeline setup completed')

        except Exception as e:
            raise WebRTCMediaError(f'Error handling media track: {str(e)}', peer_id) from e

    async def _handle_transcript(self, transcript: str, peer_id: str) -> None:
        """Handle transcript text"""
        try:
            peer = self.peer_session_manager.get_peer(peer_id)
            if peer and peer.data_channel and peer.data_channel.readyState == 'open':
                peer.data_channel.send(json.dumps({'transcript': transcript}))
                logger.info(f'Sent transcript to peer {peer_id}: {transcript}')
        except Exception as e:
            logger.error(f'Error sending transcript to peer {peer_id}: {e}')

    async def create_peer_connection(self, peer_id: str) -> None:
        """Create a new peer connection"""
        await self.peer_session_manager.create_peer(peer_id)

    async def close_peer_connection(self, peer_id: str) -> None:
        """Close a peer connection"""
        try:
            # Get peer object
            peer = self.peer_session_manager.get_peer(peer_id)
            if peer:
                # peer.cleanup() will automatically clean up audio_loop
                # Close Peer connection (this will call peer.cleanup())
                await self.peer_session_manager.close_peer(peer_id)

        except Exception as e:
            raise WebRTCPeerError(f'Error closing peer connection: {str(e)}', peer_id) from e


def get_webrtc_service() -> WebRTCService:
    """
    Get WebRTC service instance

    Returns:
        WebRTCService: Global instance of WebRTC service
    """
    if not hasattr(get_webrtc_service, '_instance'):
        get_webrtc_service._instance = WebRTCService()
    return get_webrtc_service._instance
