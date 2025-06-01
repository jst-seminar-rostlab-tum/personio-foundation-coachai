import logging
from dataclasses import dataclass
from typing import Optional

from aiortc import (
    RTCDataChannel,
    RTCIceCandidate,
    RTCPeerConnection,
    RTCSessionDescription,
)
from aiortc.contrib.media import MediaBlackhole
from fastapi import WebSocket

from ..schemas.webrtc_schema import (
    AudioControlConfig,
    WebRTCDataChannelConfig,
    WebRTCIceCandidate,
    WebRTCIceCandidateResponse,
    WebRTCSignalingMessage,
    WebRTCSignalingType,
)

# from .audio_service import AudioService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# aiortc doesn't support parsing ICE candidates from strings, this is a workaround
# https://github.com/aiortc/aiortc/issues/1084
def parse_candidate(candidate_str: str) -> dict:
    """
    Parses a WebRTC ICE candidate string into components.
    Example input:
        "candidate:370845912 1 udp 2122260223 192.168.1.5 55946 typ host"
    Returns:
        dict with keys suitable for RTCIceCandidate
    """
    parts = candidate_str.strip().split()
    if not candidate_str.startswith('candidate:') or len(parts) < 8:
        raise ValueError('Invalid ICE candidate string')

    return {
        'foundation': parts[0][len('candidate:') :],  # Remove 'candidate:' prefix
        'component': int(parts[1]),
        # 'transport': parts[2],
        'priority': int(parts[3]),
        'ip': parts[4],
        'port': int(parts[5]),
        'protocol': parts[7],
        'type': parts[7],
        # 'tcpType': None,  # Only set for TCP candidates
        # 'ttl': None,      # Not used anymore
    }


@dataclass
class Peer:
    """Peer connection and its associated resources"""

    peer_id: str
    connection: RTCPeerConnection
    audio_channel: Optional[RTCDataChannel] = None
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
        self.data_channel_config = WebRTCDataChannelConfig()
        self.default_audio_config = AudioControlConfig()

    async def _setup_peer_connection(
        self, pc: RTCPeerConnection, websocket: WebSocket, peer_id: str
    ) -> None:
        """Setup peer connection event handlers"""

        @pc.on('offer')
        async def on_offer(offer: RTCSessionDescription) -> None:
            logger.info(f'[ICE] Received offer from peer {peer_id}')
            try:
                # Set remote description
                await pc.setRemoteDescription(offer)
                logger.debug(f'Set remote description for peer {peer_id}')

                # Create answer
                answer = await pc.createAnswer()
                await pc.setLocalDescription(answer)
                logger.debug(f'Created and set local answer for peer {peer_id}')

                # Setup audio channel
                await self.accept_audio_channel(peer_id)
                logger.debug(f'Setup audio channel for peer {peer_id}')

                # Send answer to client
                await websocket.send_json(
                    WebRTCSignalingMessage(
                        type=WebRTCSignalingType.ANSWER,
                        sdp=pc.localDescription.sdp,
                    ).model_dump()
                )
                logger.info(f'[ICE] Sent answer to peer {peer_id}')
            except Exception as e:
                logger.error(f'[ICE] Failed to handle offer: {e}')

        @pc.on('iceconnectionstatechange')
        async def on_iceconnectionstatechange() -> None:
            logger.info(f'[ICE] Connection state changed to: {pc.iceConnectionState}')
            if pc.iceConnectionState == 'checking':
                logger.info('[ICE] Checking available candidates...')
            elif pc.iceConnectionState == 'failed':
                logger.error('[ICE] Connection failed - no valid candidates found')
            elif pc.iceConnectionState == 'disconnected':
                logger.warning('[ICE] Connection disconnected')
            elif pc.iceConnectionState == 'closed':
                logger.info('[ICE] Connection closed')

        @pc.on('icegatheringstatechange')
        async def on_icegatheringstatechange() -> None:
            logger.info(f'[ICE] Gathering state changed to: {pc.iceGatheringState}')
            if pc.iceGatheringState == 'gathering':
                logger.info('[ICE] Started gathering candidates')
            elif pc.iceGatheringState == 'complete':
                logger.info('[ICE] Finished gathering candidates')

        @pc.on('connectionstatechange')
        async def on_connectionstatechange() -> None:
            logger.info(f'[ICE] Connection state changed to: {pc.connectionState}')
            if pc.connectionState == 'connecting':
                logger.info('[ICE] Attempting to establish connection')
            elif pc.connectionState == 'failed':
                logger.error('[ICE] Connection failed')
            elif pc.connectionState == 'disconnected':
                logger.warning('[ICE] Connection disconnected')

        @pc.on('icecandidate')
        async def on_icecandidate(candidate: RTCIceCandidate) -> None:
            if candidate:
                logger.info(f'[ICE] New candidate found: {candidate.candidate}')
                logger.info(f'[ICE] Candidate type: {candidate.type}')
                logger.info(f'[ICE] Candidate protocol: {candidate.protocol}')
                logger.info(f'[ICE] Candidate priority: {candidate.priority}')

                # Send ICE candidate to client
                try:
                    await websocket.send_json(
                        WebRTCIceCandidateResponse(
                            type=WebRTCSignalingType.CANDIDATE,
                            candidate=WebRTCIceCandidate(
                                candidate=candidate.candidate,
                                sdpMid=candidate.sdpMid,
                                sdpMLineIndex=candidate.sdpMLineIndex,
                            ),
                        ).model_dump()
                    )
                    logger.info('[ICE] Candidate sent to client')
                except Exception as e:
                    logger.error(f'[ICE] Failed to send candidate to client: {e}')
            else:
                logger.info('[ICE] Candidate gathering completed')

    async def _setup_datachannel(self, channel: RTCDataChannel, peer_id: str, peer: Peer) -> None:
        """Setup data channel event handlers"""

        @channel.on('open')
        def on_open() -> None:
            logger.info(f'Audio channel opened for peer {peer_id}')

        @channel.on('message')
        def on_message(message: bytes) -> None:
            logger.info(f'Received audio data from peer {peer_id}, size: {len(message)} bytes')
            self.handle_audio_data(message, peer_id)
            logger.info(f'Processed audio data from peer {peer_id}, size: {len(message)} bytes')

        @channel.on('close')
        def on_close() -> None:
            logger.info(f'Audio channel closed for peer {peer_id}')
            peer.audio_channel = None

        @channel.on('error')
        def on_error(error: Exception) -> None:
            logger.error(f'Audio channel error for peer {peer_id}: {error}')

    async def _handle_datachannel_open(self, channel: RTCDataChannel, peer_id: str) -> None:
        """Handle data channel open event"""
        logger.info(f'Audio channel opened for peer {peer_id}')

    async def _handle_datachannel_message(
        self, message: bytes, peer_id: str, channel: RTCDataChannel
    ) -> None:
        """Handle data channel message event"""
        logger.info(f'Received audio data from peer {peer_id}, size: {len(message)} bytes')
        self.handle_audio_data(message, peer_id)
        logger.info(f'Processed audio data from peer {peer_id}, size: {len(message)} bytes')

    async def _handle_datachannel_close(self, peer_id: str, peer: Peer) -> None:
        """Handle data channel close event"""
        logger.info(f'Audio channel closed for peer {peer_id}')
        peer.audio_channel = None

    async def _handle_datachannel_error(self, error: Exception, peer_id: str) -> None:
        """Handle data channel error event"""
        logger.error(f'Audio channel error for peer {peer_id}: {error}')

    async def accept_audio_channel(self, peer_id: str) -> None:
        """Accept audio data channel for a peer"""
        peer = self.peers.get(peer_id)
        if not peer:
            logger.error(f'No peer found for peer {peer_id}')
            return

        try:

            @peer.connection.on('datachannel')
            def on_datachannel(channel: RTCDataChannel) -> None:
                logger.info(f'Received data channel: {channel.label}')
                peer.audio_channel = channel
                self._setup_datachannel(channel, peer_id, peer)

            logger.info(f'Audio channel accepted for peer {peer_id}')
        except Exception as e:
            logger.error(f'Error accepting audio channel for peer {peer_id}: {e}')
            raise

    def handle_audio_data(self, message: bytes, peer_id: str) -> None:
        """Handle incoming audio data"""
        try:
            peer = self.peers.get(peer_id)
            if not peer:
                logger.error(f'No peer found for peer {peer_id}')
                return

            # Use audio service to process data with the configured parameters
            # await self.audio_service.write_audio_data(
            #     peer_id,
            #     message,
            #     sample_rate=peer.audio_config.sample_rate,
            #     buffer_size=peer.audio_config.buffer_size,
            # )

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
            # await self.audio_service.cleanup(peer_id)
            del self.peers[peer_id]
            logger.debug(f'Cleaned up peer connection for peer {peer_id}')

    async def create_peer_connection(
        self, websocket: WebSocket, peer_id: str, audio_config: Optional[AudioControlConfig] = None
    ) -> None:
        """Create a new peer connection"""
        # Create new peer connection
        pc = RTCPeerConnection()

        # Setup event handlers
        await self._setup_peer_connection(pc, websocket, peer_id)

        # Use the provided audio config or the default config
        audio_config = audio_config or self.default_audio_config

        self.peers[peer_id] = Peer(
            peer_id=peer_id,
            connection=pc,
            audio_config=audio_config,
        )
        logger.debug(
            f'Created new peer connection for peer {peer_id} with audio config: {audio_config}'
        )


def get_webrtc_service() -> WebRTCService:
    """
    Get WebRTC service instance

    Returns:
        WebRTCService: Global instance of WebRTC service
    """
    if not hasattr(get_webrtc_service, '_instance'):
        get_webrtc_service._instance = WebRTCService()
    return get_webrtc_service._instance
