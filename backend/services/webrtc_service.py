import logging
from dataclasses import dataclass
from typing import Optional

from aiortc import (
    RTCPeerConnection,
    RTCRtpTransceiver,
)
from aiortc.mediastreams import MediaStreamTrack
from fastapi import WebSocket

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Peer:
    """Peer connection and its associated resources"""

    peer_id: str
    connection: RTCPeerConnection
    transceiver: Optional[RTCRtpTransceiver] = None

    async def cleanup(self) -> None:
        """Cleanup all resources associated with this peer"""
        if self.transceiver:
            self.transceiver.stop()
        await self.connection.close()


class WebRTCService:
    """WebRTC service for handling peer connections"""

    def __init__(self) -> None:
        """Initialize the WebRTC service"""
        self.peers: dict[str, Peer] = {}

    async def create_peer_connection(self, websocket: WebSocket, peer_id: str) -> None:
        """Create a new peer connection"""
        if peer_id in self.peers:
            logger.info(f'Peer {peer_id} already exists, closing old connection')
            await self.peers[peer_id].connection.close()
            del self.peers[peer_id]

        pc = RTCPeerConnection()
        transceiver = pc.addTransceiver('audio', direction='sendrecv')
        logger.info(f'Created transceiver for peer {peer_id}')

        self.peers[peer_id] = Peer(connection=pc, peer_id=peer_id, transceiver=transceiver)

        @pc.on('track')
        async def on_track(track: MediaStreamTrack) -> None:
            logger.info(f'Track {track.kind} received')
            if track.kind == 'audio':
                logger.info('Audio track received, sending back to client')

                # TODO: send audio to LLM
                self.peers[peer_id].transceiver.sender.replaceTrack(track)
                logger.info('Audio track sent back to client')

        @pc.on('connectionstatechange')
        async def on_connectionstatechange() -> None:
            logger.info(f'Connection state is {pc.connectionState}')
            if pc.connectionState == 'failed':
                await pc.close()
                del self.peers[peer_id]

        @pc.on('iceconnectionstatechange')
        async def on_iceconnectionstatechange() -> None:
            logger.info(f'ICE connection state is {pc.iceConnectionState}')
            if pc.iceConnectionState == 'failed':
                await pc.close()
                del self.peers[peer_id]

        @pc.on('signalingstatechange')
        async def on_signalingstatechange() -> None:
            logger.info(f'Signaling state is {pc.signalingState}')

        logger.info(f'Peer connection created for peer {peer_id}')

    async def close_peer_connection(self, peer_id: str) -> None:
        """Close a peer connection"""
        if peer_id in self.peers:
            await self.peers[peer_id].connection.close()
            del self.peers[peer_id]
            logger.info(f'Peer connection closed for peer {peer_id}')


def get_webrtc_service() -> WebRTCService:
    """
    Get WebRTC service instance

    Returns:
        WebRTCService: Global instance of WebRTC service
    """
    if not hasattr(get_webrtc_service, '_instance'):
        get_webrtc_service._instance = WebRTCService()
    return get_webrtc_service._instance
