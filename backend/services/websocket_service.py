import logging
from fastapi import WebSocket
from aiortc import RTCSessionDescription
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
                pc = self.webrtc_service.peers[peer_id].connection
                await pc.setRemoteDescription(
                    RTCSessionDescription(sdp=message.sdp, type=WebRTCSignalingType.OFFER)
                )
        except Exception as e:
            logger.error(f'Error handling WebRTC message: {e}')
            await self.close_connection(websocket)

    async def close_connection(self, websocket: WebSocket) -> None:
        """Close WebSocket connection and cleanup resources"""
        try:
            await self.webrtc_service.cleanup(websocket)
            await websocket.close()
        except Exception as e:
            logger.error(f'Error closing connection: {e}')


def get_websocket_service() -> WebSocketService:
    """
    Get WebSocket service instance

    Returns:
        WebSocketService: Global instance of WebSocket service
    """
    if not hasattr(get_websocket_service, '_instance'):
        get_websocket_service._instance = WebSocketService()
    return get_websocket_service._instance
