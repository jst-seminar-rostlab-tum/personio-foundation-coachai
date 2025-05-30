import asyncio
import logging
from dataclasses import dataclass
from typing import Optional

from aiortc import RTCDataChannel, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaBlackhole
from fastapi import WebSocket

from ..schemas.webrtc_schema import (
    AudioControlConfig,
    WebRTCDataChannelConfig,
    WebRTCIceCandidateResponse,
    WebRTCSignalingMessage,
    WebRTCSignalingType,
)
from .audio_service import AudioService

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@dataclass
class Peer:
    """Peer connection and its associated resources"""

    peer_id: str
    connection: RTCPeerConnection
    audio_channel: Optional[RTCDataChannel] = None
    channel_ready: asyncio.Event = None
    audio_config: Optional[AudioControlConfig] = None

    async def cleanup(self) -> None:
        """Cleanup all resources associated with this peer"""
        if self.audio_channel:
            self.audio_channel.close()
        await self.connection.close()


class WebRTCService:
    """WebRTC service for audio transmission"""

    def __init__(self) -> None:
        """Initialize the WebRTC service"""
        self.media_blackhole = MediaBlackhole()
        self.peers: dict[str, Peer] = {}
        self.audio_service = AudioService()
        self.data_channel_config = WebRTCDataChannelConfig()
        self.default_audio_config = AudioControlConfig()

    async def handle_signaling(
        self, message: WebRTCSignalingMessage, websocket: WebSocket
    ) -> Optional[WebRTCSignalingMessage]:
        """
        Handle WebRTC signaling messages

        Args:
            message: Signaling message data
            websocket: WebSocket connection

        Returns:
            Optional[WebRTCSignalingMessage]: Response to be sent to the client
        """
        peer_id = str(id(websocket))
        logger.debug(f'Received message type: {message.type} from peer {peer_id}')

        if message.type == WebRTCSignalingType.OFFER:
            # Create new peer connection
            pc = RTCPeerConnection()
            channel_ready = asyncio.Event()

            # Use the audio config from the message or the default config
            audio_config = message.audio_config or self.default_audio_config

            self.peers[peer_id] = Peer(
                peer_id=peer_id,
                connection=pc,
                channel_ready=channel_ready,
                audio_config=audio_config,
            )
            logger.debug(
                f'Created new peer connection for peer {peer_id} with audio config: {audio_config}'
            )

            # Set remote description
            await pc.setRemoteDescription(
                RTCSessionDescription(sdp=message.sdp, type=WebRTCSignalingType.OFFER)
            )
            logger.debug(f'Set remote description for peer {peer_id}')

            # Create answer
            answer = await pc.createAnswer()
            await pc.setLocalDescription(answer)
            logger.debug(f'Created and set local answer for peer {peer_id}')

            # Setup audio channel and wait for it to be ready
            await self.setup_audio_channel(peer_id)
            logger.debug(f'Setup audio channel for peer {peer_id}')

            # Wait for channel to be ready
            try:
                await asyncio.wait_for(channel_ready.wait(), timeout=10.0)
                logger.debug(f'Audio channel ready for peer {peer_id}')
            except asyncio.TimeoutError:
                logger.error(f'Timeout waiting for audio channel to be ready for peer {peer_id}')
                return None

            # Only return answer after audio channel is ready
            return WebRTCSignalingMessage(
                type=WebRTCSignalingType.ANSWER,
                sdp=pc.localDescription.sdp,
                audio_config=audio_config,
            )

        elif message.type == WebRTCSignalingType.CANDIDATE:
            peer = self.peers.get(peer_id)
            if peer:
                await peer.connection.addIceCandidate({
                    'candidate': message.candidate.candidate,
                    'sdpMid': message.candidate.sdp_mid,
                    'sdpMLineIndex': message.candidate.sdp_mline_index,
                    'usernameFragment': getattr(message.candidate, 'usernameFragment', None),
                })
                logger.debug(f'Added ICE candidate for peer {peer_id}')
                return WebRTCSignalingMessage(
                    type=WebRTCSignalingType.CANDIDATE,
                    candidate_response=WebRTCIceCandidateResponse(
                        status='success', message='ICE candidate added successfully'
                    ),
                )
            else:
                logger.error(f'No peer found for peer {peer_id}')
                return WebRTCSignalingMessage(
                    type=WebRTCSignalingType.CANDIDATE,
                    candidate_response=WebRTCIceCandidateResponse(
                        status='error', message='No peer connection found'
                    ),
                )

        return None

    async def setup_audio_channel(self, peer_id: str) -> None:
        """Setup audio data channel for a peer"""
        peer = self.peers.get(peer_id)
        if not peer:
            logger.error(f'No peer found for peer {peer_id}')
            return

        try:
            # Create audio file with the configured sample rate
            await self.audio_service.create_audio_file(
                peer_id, sample_rate=peer.audio_config.sample_rate
            )

            # Create audio data channel using configuration
            audio_channel = peer.connection.createDataChannel(
                self.data_channel_config.label,
                ordered=self.data_channel_config.ordered,
                maxRetransmits=self.data_channel_config.max_retransmits,
                protocol=self.data_channel_config.protocol,
                negotiated=self.data_channel_config.negotiated,
                id=self.data_channel_config.id,
            )

            # Set event handlers
            @audio_channel.on('open')
            def on_open() -> None:
                logger.info(f'Audio channel opened for peer {peer_id}')
                # Send audio configuration
                audio_channel.send(peer.audio_config.model_dump_json())
                peer.channel_ready.set()  # Set channel ready event

            @audio_channel.on('message')
            def on_message(message: bytes) -> None:
                self.handle_audio_data(message, peer_id)

            @audio_channel.on('close')
            def on_close() -> None:
                logger.info(f'Audio channel closed for peer {peer_id}')
                if peer_id in self.peers:
                    self.peers[peer_id].audio_channel = None
                    # Clean up audio resources
                    asyncio.create_task(self.audio_service.cleanup(peer_id))

            @audio_channel.on('error')
            def on_error(error: Exception) -> None:
                logger.error(f'Audio channel error for peer {peer_id}: {error}')

            peer.audio_channel = audio_channel
            logger.info(f'Audio channel setup completed for peer {peer_id}')
        except Exception as e:
            logger.error(f'Error setting up audio channel for peer {peer_id}: {e}')
            raise

    async def handle_audio_data(self, message: bytes, peer_id: str) -> None:
        """Handle incoming audio data"""
        try:
            peer = self.peers.get(peer_id)
            if not peer:
                logger.error(f'No peer found for peer {peer_id}')
                return

            # Use audio service to process data with the configured parameters
            await self.audio_service.write_audio_data(
                peer_id,
                message,
                sample_rate=peer.audio_config.sample_rate,
                buffer_size=peer.audio_config.buffer_size,
            )
            logger.debug(f'Processed audio data from peer {peer_id}, size: {len(message)} bytes')

        except Exception as e:
            logger.error(f'Error handling audio data from peer {peer_id}: {e}')
            logger.exception(e)

    async def cleanup(self, websocket: WebSocket) -> None:
        """
        Clean up WebRTC connection

        Args:
            websocket: WebSocket connection to clean up
        """
        peer_id = str(id(websocket))
        if peer_id in self.peers:
            peer = self.peers[peer_id]
            await peer.cleanup()
            # Clean up audio resources
            await self.audio_service.cleanup(peer_id)
            del self.peers[peer_id]
            logger.debug(f'Cleaned up peer connection for peer {peer_id}')


def get_webrtc_service() -> WebRTCService:
    """
    Get WebRTC service instance

    Returns:
        WebRTCService: Global instance of WebRTC service
    """
    if not hasattr(get_webrtc_service, '_instance'):
        get_webrtc_service._instance = WebRTCService()
    return get_webrtc_service._instance
