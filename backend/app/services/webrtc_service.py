import asyncio
import json
import logging
import time
from dataclasses import dataclass

from aiortc import (
    RTCConfiguration,
    RTCDataChannel,
    RTCIceServer,
    RTCPeerConnection,
    RTCRtpTransceiver,
)
from aiortc.mediastreams import MediaStreamTrack
from google.genai.live import AsyncSession

from app.connections.gemnini_client import DEFAULT_MODEL, LIVE_CONFIG, get_client
from app.schemas.webrtc_schema import (
    GEMINI_SAMPLE_RATE,
    GeminiAudioChunk,
    WebRTCDataChannelError,
    WebRTCMediaError,
    WebRTCPeerError,
)
from app.services.audio_processor import pcm_to_opus, resample_audio

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

    async def cleanup(self) -> None:
        """Cleanup all resources associated with this peer"""
        if self.transceiver:
            self.transceiver.stop()
        if self.data_channel:
            self.data_channel.close()
        await self.connection.close()


class WebRTCService:
    """WebRTC service for handling peer connections"""

    def __init__(self) -> None:
        """Initialize the WebRTC service"""
        self.peers: dict[str, Peer] = {}
        self.client = get_client()

    async def _register_rtc_connection(self, peer_id: str) -> None:
        """Register RTC connection, return Peer instance"""
        if peer_id in self.peers:
            logger.debug(f'Peer {peer_id} already exists, closing old connection')
            await self.peers[peer_id].connection.close()
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
            try:
                logger.info(f'[DataChannel] Received data channel: {channel.label}')
                logger.debug(f'[DataChannel] Channel state: {channel.readyState}')
                logger.debug(f'[DataChannel] Channel protocol: {channel.protocol}')
                logger.debug(f'[DataChannel] Channel negotiated: {channel.negotiated}')
                logger.debug(f'[DataChannel] Channel id: {channel.id}')

                if channel.label == 'transcript':

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
                raise WebRTCDataChannelError(
                    f'Error handling data channel: {str(e)}', peer_id
                ) from e

        @pc.on('track')
        async def on_track(track: MediaStreamTrack) -> None:
            try:
                logger.info(f'Track {track.kind} received')
                if track.kind == 'audio':
                    logger.info('Audio track received, sending back to client')
                    # self.peers[peer_id].transceiver.sender.replaceTrack(track)
                    await self._handle_audio_track(track, peer_id)
                    logger.debug('Audio track sent back to client')
            except Exception as e:
                raise WebRTCMediaError(f'Error handling media track: {str(e)}', peer_id) from e

        peer = Peer(connection=pc, peer_id=peer_id, transceiver=transceiver)
        self.peers[peer_id] = peer
        logger.info(f'Peer connection created for peer {peer_id}')

    async def _handle_audio_track(self, track: MediaStreamTrack, peer_id: str) -> None:
        """Handle audio track"""
        # Send Opus data to Gemini
        async with self.client.aio.live.connect(model=DEFAULT_MODEL, config=LIVE_CONFIG) as session:
            asyncio.create_task(self._process_audio_frames(track, session, peer_id))
            async for response in session.receive():
                logger.info(f'Received response from Gemini: {response}')
                # convert response to pcm
                if response.data:
                    pcm_data = response.data
                    # resample pcm data
                    pcm_data = resample_audio(pcm_data, GEMINI_SAMPLE_RATE, track.sample_rate)
                    # convert pcm data to opus
                    opus_data = pcm_to_opus(pcm_data)
                    # send opus data to client
                    # TODO: fix MediaStreamTrack with av
                    self.peers[peer_id].transceiver.sender.replaceTrack(
                        MediaStreamTrack(opus_data, sample_rate=track.sample_rate)
                    )
                if response.text:
                    transcript = response.text
                    self.peers[peer_id].data_channel.send(json.dumps({'transcript': transcript}))

    async def create_peer_connection(self, peer_id: str) -> None:
        """Create a new peer connection"""
        await self._register_rtc_connection(peer_id)

    async def close_peer_connection(self, peer_id: str) -> None:
        """Close a peer connection"""
        try:
            if peer_id in self.peers:
                await self.peers[peer_id].cleanup()
                del self.peers[peer_id]
                logger.info(f'Peer connection closed for peer {peer_id}')
        except Exception as e:
            raise WebRTCPeerError(f'Error closing peer connection: {str(e)}', peer_id) from e

    async def _process_audio_frames(
        self,
        track: MediaStreamTrack,
        session: AsyncSession,
        peer_id: str,
    ) -> None:
        """Process incoming audio frames and send to Gemini"""
        try:
            while True:
                # Receive audio frame
                frame = await track.recv()

                # Convert frame to bytes (this depends on your audio processing implementation)
                audio_bytes = frame.to_bytes()  # You'll need to implement this

                # Resample if needed
                if frame.sample_rate != GEMINI_SAMPLE_RATE:
                    audio_bytes = resample_audio(audio_bytes, frame.sample_rate, GEMINI_SAMPLE_RATE)

                # Convert to format expected by Gemini (Opus or PCM)
                processed_audio = pcm_to_opus(audio_bytes)

                # Send to Gemini
                audio_chunk = GeminiAudioChunk(
                    data=processed_audio, timestamp=time.time(), sample_rate=GEMINI_SAMPLE_RATE
                )
                session.send_realtime_input(audio=audio_chunk.data)

        except Exception as e:
            logger.error(f'Error processing audio frames for peer {peer_id}: {e}')


def get_webrtc_service() -> WebRTCService:
    """
    Get WebRTC service instance

    Returns:
        WebRTCService: Global instance of WebRTC service
    """
    if not hasattr(get_webrtc_service, '_instance'):
        get_webrtc_service._instance = WebRTCService()
    return get_webrtc_service._instance
