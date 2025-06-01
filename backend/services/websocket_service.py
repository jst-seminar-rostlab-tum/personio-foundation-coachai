import logging

from aiortc import RTCSessionDescription, RTCIceCandidate
from fastapi import WebSocket

from ..schemas.webrtc_schema import WebRTCSignalingMessage, WebRTCSignalingType, WebRTCIceCandidate
from .webrtc_service import get_webrtc_service

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

        if message.type == WebRTCSignalingType.OFFER:
            # always create/overwrite peer connection, ensure peer is the latest
            await self.webrtc_service.create_peer_connection(websocket, peer_id)
            pc = self.webrtc_service.peers[peer_id].connection
            await pc.setRemoteDescription(
                RTCSessionDescription(sdp=message.sdp, type=WebRTCSignalingType.OFFER)
            )
            # Create answer and set local description
            answer = await pc.createAnswer()
            await pc.setLocalDescription(answer)

            # send answer to client
            await websocket.send_json(
                WebRTCSignalingMessage(
                    type=WebRTCSignalingType.ANSWER,
                    sdp=answer.sdp,
                ).model_dump()
            )

        elif message.type == WebRTCSignalingType.CANDIDATE:
            peer = self.webrtc_service.peers.get(peer_id)
            if not peer:
                logger.error(f'No peer found for candidate, peer_id={peer_id}')
                return
            candidate = message.candidate
            if candidate:
                rtc_candidate = self._build_rtc_ice_candidate(candidate)
                logger.info(f'Adding ICE candidate for peer {peer_id}: {rtc_candidate}')
                await peer.connection.addIceCandidate(rtc_candidate)
            else:
                logger.warning(f'Received candidate message with no candidate for peer_id={peer_id}')

        else:
            logger.warning(f'Unknown signaling message type: {message.type}')

    def _build_rtc_ice_candidate(self, candidate_obj: WebRTCIceCandidate) -> RTCIceCandidate:
        """
        Build RTCIceCandidate from candidate object, using parse_candidate if candidate is a string.
        """
        if hasattr(candidate_obj, 'candidate') and isinstance(candidate_obj.candidate, str):
            parts = candidate_obj.candidate.strip().split()
            return RTCIceCandidate(
                sdpMid=candidate_obj.sdp_mid,
                sdpMLineIndex=candidate_obj.sdp_mline_index,
                component=int(parts[1]),
                foundation=parts[0][len('candidate:') :],
                ip=parts[4],
                port=int(parts[5]),
                priority=int(parts[3]),
                protocol=parts[7],
                type=parts[7],
            )
        else:
            raise ValueError('Invalid candidate object')

def get_websocket_service() -> WebSocketService:
    """
    Get WebSocket service instance

    Returns:
        WebSocketService: Global instance of WebSocket service
    """
    if not hasattr(get_websocket_service, '_instance'):
        get_websocket_service._instance = WebSocketService()
    return get_websocket_service._instance
