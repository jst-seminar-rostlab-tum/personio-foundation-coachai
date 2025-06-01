import logging

from aiortc import RTCSessionDescription
from fastapi import WebSocket

from ..schemas.webrtc_schema import WebRTCSignalingMessage, WebRTCSignalingType
from .webrtc_service import get_webrtc_service

logger = logging.getLogger(__name__)


class WebSocketService:
    """WebSocket connection service"""

    def __init__(self) -> None:
        """Initialize the WebSocket service"""
        self.webrtc_service = get_webrtc_service()

    async def handle_webrtc_message(
        self, websocket: WebSocket, message: WebRTCSignalingMessage
    ) -> None:
        """Handle WebRTC signaling messages"""
        peer_id = str(id(websocket))
        try:
            if message.type == WebRTCSignalingType.OFFER:
                if peer_id not in self.webrtc_service.peers:
                    # Create peer connection if not exists
                    await self.webrtc_service.create_peer_connection(websocket, peer_id)
                pc = self.webrtc_service.peers[peer_id].connection
                logger.info(f'Setting remote description for peer {peer_id}')
                await pc.setRemoteDescription(
                    RTCSessionDescription(sdp=message.sdp, type=WebRTCSignalingType.OFFER)
                )
        # TODO: use dedicated error handler
        except Exception as e:
            logger.error(f'Error handling WebRTC message: {e}')
            await self.webrtc_service.cleanup(websocket)

def get_websocket_service() -> WebSocketService:
    """
    Get WebSocket service instance

    Returns:
        WebSocketService: Global instance of WebSocket service
    """
    if not hasattr(get_websocket_service, '_instance'):
        get_websocket_service._instance = WebSocketService()
    return get_websocket_service._instance
