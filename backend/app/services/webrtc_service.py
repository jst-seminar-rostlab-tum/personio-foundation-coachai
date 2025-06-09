from __future__ import annotations

import asyncio
import contextlib
import json
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from aiortc import (
    RTCConfiguration,
    RTCDataChannel,
    RTCIceServer,
    RTCPeerConnection,
    RTCRtpTransceiver,
)
from aiortc.mediastreams import MediaStreamTrack
from google import genai
from google.genai.live import AsyncSession

from app.connections.gemnini_client import LIVE_CONFIG, MODEL, get_client
from app.schemas.webrtc_schema import (
    GEMINI_SAMPLE_RATE,
    WebRTCDataChannelError,
    WebRTCMediaError,
    WebRTCPeerError,
)
from app.services.audio_processor import AudioStreamTrack, pcm_to_opus, resample_audio

logger = logging.getLogger(__name__)


RTC_CONFIG = RTCConfiguration(
    iceServers=[
        RTCIceServer(
            urls=[
                'stun:stun.l.google.com:19302',
            ]
        ),
    ]
)


@dataclass
class Peer:
    """Peer connection and its associated resources"""

    peer_id: str
    connection: RTCPeerConnection
    transceiver: RTCRtpTransceiver | None = None
    data_channel: RTCDataChannel | None = None
    audio_loop: WebRTCAudioLoop | None = None

    async def cleanup(self) -> None:
        """Cleanup all resources associated with this peer"""
        # Clean up audio loop if present
        if self.audio_loop:
            await self.audio_loop.stop()
            self.audio_loop = None
        # Clean up transceiver
        if self.transceiver:
            self.transceiver.stop()
        # Clean up data channel
        if self.data_channel:
            self.data_channel.close()
        # Close peer connection
        await self.connection.close()


class PeerManager:
    """Manage the lifecycle of WebRTC Peer connections"""

    def __init__(self) -> None:
        self.peers: dict[str, Peer] = {}
        self.on_track_callback: Callable | None = None
        self.on_datachannel_callback: Callable | None = None

    def set_track_callback(self, callback: Callable) -> None:
        """Set callback for track events"""
        self.on_track_callback = callback

    def set_datachannel_callback(self, callback: Callable) -> None:
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
        self.audio_in_queue: asyncio.Queue | None = None  # Audio received from Gemini
        self.audio_out_queue: asyncio.Queue | None = None  # Audio to send to Gemini

        # TaskGroup for managing tasks
        self._tg: asyncio.TaskGroup | None = None
        self._main_task: asyncio.Task | None = None

        # WebRTC specific attributes
        self.webrtc_track: MediaStreamTrack | None = None
        self.peer: Peer | None = None

        # Callback for transcript handling
        self.on_transcript_callback: Callable | None = None

    def set_transcript_callback(self, callback: Callable) -> None:
        """Set callback for transcript handling"""
        self.on_transcript_callback = callback

    async def start(self, webrtc_track: MediaStreamTrack, peer: Peer) -> None:
        """Start audio stream processing, use TaskGroup"""

        self.webrtc_track = webrtc_track
        self.peer = peer

        # Initialize queues
        self.audio_in_queue = asyncio.Queue()
        self.audio_out_queue = asyncio.Queue(maxsize=5)

        self._main_task = asyncio.create_task(self._run_tasks())

        logger.info(f'WebRTC Audio Loop started for peer {self.peer_id}')

    async def _run_tasks(self) -> None:
        try:
            async with asyncio.TaskGroup() as tg:
                tg.create_task(self._listen_webrtc_audio())
                tg.create_task(self._send_realtime())
                tg.create_task(self._play_webrtc_audio())
        except Exception as e:
            logger.error(f'WebRTCAudioLoop main task error for peer {self.peer_id}: {e}')

    async def stop(self) -> None:
        """Stop audio stream processing, TaskGroup cleanup"""

        with contextlib.suppress(asyncio.CancelledError):
            await self._main_task

        if self.audio_in_queue:
            while not self.audio_in_queue.empty():
                try:
                    self.audio_in_queue.get_nowait()
                except asyncio.QueueEmpty:
                    break

        logger.info(f'WebRTC Audio Loop stopped for peer {self.peer_id}')

    async def _listen_webrtc_audio(self) -> None:
        """Capture audio from WebRTC, replaces AudioLoop.listen_audio()"""
        try:
            while True:
                try:
                    # Receive audio frame
                    frame = await self.webrtc_track.recv()
                    print('Received frame:', frame)

                    # Convert to bytes
                    audio_array = frame.to_ndarray()
                    audio_bytes = audio_array.tobytes()

                    # Resample to Gemini required sample rate
                    if frame.rate != GEMINI_SAMPLE_RATE:
                        audio_bytes = resample_audio(audio_bytes, frame.rate, GEMINI_SAMPLE_RATE)

                    # Put into queue, similar to AudioLoop
                    await self.audio_out_queue.put({'data': audio_bytes, 'mime_type': 'audio/pcm'})

                except StopAsyncIteration:
                    logger.info(f'Audio track ended for peer {self.peer_id}')
                    break
        except asyncio.CancelledError:
            logger.info(f'Audio track ended for peer {self.peer_id}')
            raise

    async def _send_realtime(self) -> None:
        """Send audio to Gemini, inspired by AudioLoop.send_realtime()"""
        try:
            while self.audio_out_queue:
                # Get audio data from queue
                audio_msg = await self.audio_out_queue.get()

                # Use callback/event mechanism to notify external GeminiSessionManager
                if hasattr(self, '_send_to_gemini_callback') and self._send_to_gemini_callback:
                    await self._send_to_gemini_callback(audio_msg)

        except Exception as e:
            logger.error(f'Error in sending audio to Gemini for peer {self.peer_id}: {e}')

    async def _play_webrtc_audio(self) -> None:
        """Play audio to WebRTC, replaces AudioLoop.play_audio()"""
        try:
            while self.audio_in_queue and self.peer:
                # Get PCM data from queue
                pcm_data = await self.audio_in_queue.get()

                # Resample to WebRTC sample rate
                track_sample_rate = 48000  # Common WebRTC sample rate
                resampled_pcm = resample_audio(pcm_data, GEMINI_SAMPLE_RATE, track_sample_rate)

                # Convert to Opus
                opus_data = pcm_to_opus(resampled_pcm)

                # Send to WebRTC client
                if self.peer.transceiver and self.peer.transceiver.sender:
                    audio_track = AudioStreamTrack(opus_data, sample_rate=track_sample_rate)
                    self.peer.transceiver.sender.replaceTrack(audio_track)

        except Exception as e:
            logger.error(f'Error in playing WebRTC audio for peer {self.peer_id}: {e}')

    def set_send_to_gemini_callback(self, callback: Callable[[dict], Awaitable[None]]) -> None:
        """Set callback for sending audio to Gemini"""
        self._send_to_gemini_callback = callback

    async def receive_audio_from_gemini(self, audio_data: bytes) -> None:
        """Receive audio data from Gemini"""
        if self.audio_in_queue:
            await self.audio_in_queue.put(audio_data)

    async def handle_transcript(self, transcript: str) -> None:
        """Handle transcript text"""
        if self.on_transcript_callback:
            await self.on_transcript_callback(transcript, self.peer_id)


class GeminiSessionManager:
    """Manage Gemini API session and audio interaction, integrating AudioLoop logic"""

    def __init__(self) -> None:
        self.client: genai.Client = get_client()
        self.sessions: dict[str, AsyncSession] = {}
        self.session_tasks: dict[str, list[asyncio.Task]] = {}
        self.audio_loops: dict[str, WebRTCAudioLoop] = {}

    async def create_session(self, peer_id: str, audio_loop: WebRTCAudioLoop) -> AsyncSession:
        """Create Gemini session for the specified peer"""
        if peer_id in self.sessions:
            await self.close_session(peer_id)

        # Establish connection, inspired by AudioLoop
        session = await self.client.aio.live.connect(model=MODEL, config=LIVE_CONFIG).__aenter__()
        self.sessions[peer_id] = session
        self.session_tasks[peer_id] = []
        self.audio_loops[peer_id] = audio_loop

        # Set callback
        async def send_to_gemini_callback(audio_msg: dict) -> None:
            await self._send_audio_to_gemini(session, audio_msg)

        audio_loop.set_send_to_gemini_callback(send_to_gemini_callback)

        # Start receiving task, inspired by AudioLoop.receive_audio()
        receive_task = asyncio.create_task(
            self._receive_audio_from_gemini(session, audio_loop, peer_id)
        )
        self.session_tasks[peer_id].append(receive_task)

        logger.info(f'Gemini session created for peer {peer_id}')
        return session

    async def close_session(self, peer_id: str) -> None:
        """Close Gemini session for the specified peer"""
        if peer_id in self.sessions:
            # Cancel tasks
            if peer_id in self.session_tasks:
                for task in self.session_tasks[peer_id]:
                    if not task.done():
                        task.cancel()

                # Wait for all tasks to finish
                if self.session_tasks[peer_id]:
                    await asyncio.gather(*self.session_tasks[peer_id], return_exceptions=True)

                del self.session_tasks[peer_id]

            # Clean up audio loop reference
            if peer_id in self.audio_loops:
                del self.audio_loops[peer_id]

            # Close session
            session = self.sessions[peer_id]
            try:
                await session.__aexit__(None, None, None)
            except Exception as e:
                logger.error(f'Error closing Gemini session for peer {peer_id}: {e}')

            del self.sessions[peer_id]
            logger.info(f'Gemini session closed for peer {peer_id}')

    async def _send_audio_to_gemini(self, session: AsyncSession, audio_msg: dict) -> None:
        """Send audio to Gemini, inspired by AudioLoop sending logic"""
        try:
            await session.send(input=audio_msg)
        except Exception as e:
            logger.error(f'Error sending audio to Gemini: {e}')

    async def _receive_audio_from_gemini(
        self, session: AsyncSession, audio_loop: WebRTCAudioLoop, peer_id: str
    ) -> None:
        """Receive audio from Gemini, inspired by AudioLoop.receive_audio()"""
        try:
            input_transcription = []
            output_transcription = []

            turn = session.receive()
            async for response in turn:
                # Handle audio data
                if data := response.data:
                    await audio_loop.receive_audio_from_gemini(data)
                    continue

                # Handle transcript text
                if text := response.text:
                    print(text, end='')

                # Handle input transcription
                if response.server_content.input_transcription:
                    input_transcription.append(response.server_content.input_transcription.text)

                # Handle output transcription
                if response.server_content.output_transcription:
                    output_transcription.append(response.server_content.output_transcription.text)

                # Handle interruption, inspired by AudioLoop interruption logic
                if response.server_content.interrupted is True:
                    logger.info(f'Response interrupted for peer {peer_id}')
                    # Clear audio queue
                    if audio_loop.audio_in_queue:
                        while not audio_loop.audio_in_queue.empty():
                            try:
                                audio_loop.audio_in_queue.get_nowait()
                            except asyncio.QueueEmpty:
                                break

            # Log transcription results
            if input_transcription:
                logger.info(f'Input transcript for peer {peer_id}: {"".join(input_transcription)}')
            if output_transcription:
                logger.info(
                    f'Output transcript for peer {peer_id}: {"".join(output_transcription)}'
                )
                await audio_loop.handle_transcript(''.join(output_transcription))

        except Exception as e:
            logger.error(f'Error receiving audio from Gemini for peer {peer_id}: {e}')


class WebRTCService:
    """Business orchestration layer for WebRTC service"""

    def __init__(self) -> None:
        """Initialize the WebRTC service"""
        self.peer_manager = PeerManager()
        self.gemini_manager = GeminiSessionManager()

        # Set callbacks
        self.peer_manager.set_track_callback(self._handle_audio_track)
        self.peer_manager.set_datachannel_callback(self._handle_data_channel)

    async def _handle_data_channel(self, channel: RTCDataChannel, peer_id: str) -> None:
        """Handle data channel events"""
        try:
            logger.info(f'[DataChannel] Received data channel: {channel.label}')
            logger.debug(f'[DataChannel] Channel state: {channel.readyState}')
            logger.debug(f'[DataChannel] Channel protocol: {channel.protocol}')
            logger.debug(f'[DataChannel] Channel negotiated: {channel.negotiated}')
            logger.debug(f'[DataChannel] Channel id: {channel.id}')

            if channel.label == 'transcript':
                peer = self.peer_manager.get_peer(peer_id)
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
                logger.info('Audio track received, setting up WebRTC Audio Loop pipeline')

                # Get peer object
                peer = self.peer_manager.get_peer(peer_id)
                if not peer:
                    raise WebRTCPeerError(f'Peer {peer_id} not found', peer_id)

                # Create WebRTC Audio Loop
                audio_loop = WebRTCAudioLoop(peer_id)

                # Register to Peer object
                peer.audio_loop = audio_loop

                # Set transcript callback
                audio_loop.set_transcript_callback(self._handle_transcript)

                # Start audio loop
                await audio_loop.start(track, peer)

                # Create Gemini session
                await self.gemini_manager.create_session(peer_id, audio_loop)

                logger.debug('WebRTC Audio Loop pipeline setup completed')

        except Exception as e:
            raise WebRTCMediaError(f'Error handling media track: {str(e)}', peer_id) from e

    async def _handle_transcript(self, transcript: str, peer_id: str) -> None:
        """Handle transcript text"""
        try:
            peer = self.peer_manager.get_peer(peer_id)
            if peer and peer.data_channel:
                peer.data_channel.send(json.dumps({'transcript': transcript}))
                logger.info(f'Sent transcript to peer {peer_id}: {transcript}')
        except Exception as e:
            logger.error(f'Error sending transcript to peer {peer_id}: {e}')

    async def create_peer_connection(self, peer_id: str) -> None:
        """Create a new peer connection"""
        await self.peer_manager.create_peer(peer_id)

    async def close_peer_connection(self, peer_id: str) -> None:
        """Close a peer connection"""
        try:
            # Get peer object
            peer = self.peer_manager.get_peer(peer_id)
            if peer:
                # Close Gemini session
                # (this will also clean up audio_loop reference in session_manager)
                await self.gemini_manager.close_session(peer_id)

                # peer.cleanup() will automatically clean up audio_loop
                # Close Peer connection (this will call peer.cleanup())
                await self.peer_manager.close_peer(peer_id)

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
