import logging

from aiortc import RTCIceCandidate, RTCSessionDescription
from fastapi import WebSocket

from ..schemas.webrtc_schema import WebRTCIceCandidate, WebRTCSignalingMessage, WebRTCSignalingType
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

            # set remote description
            logger.info(f'Received offer SDP: {message.sdp}')
            await pc.setRemoteDescription(
                RTCSessionDescription(sdp=message.sdp, type=WebRTCSignalingType.OFFER)
            )
            logger.info(f'Remote description set for peer {peer_id}')

            # Create answer and set local description
            answer = await pc.createAnswer()
            logger.info(f'Created answer SDP: {answer.sdp}')
            
            # Check if data channel is in the offer
            if 'm=application' in message.sdp:
                logger.info('Data channel found in offer SDP')
            else:
                logger.warning('Data channel not found in offer SDP')
            
            # Ensure data channel is included in the answer
            if 'm=application' not in answer.sdp:
                logger.warning('Data channel not found in answer SDP, adding it manually')
                sdp_lines = answer.sdp.split('\n')
                # Add data channel media line after the last media line
                for i, line in enumerate(sdp_lines):
                    if line.startswith('m='):
                        last_media_index = i
                sdp_lines.insert(last_media_index + 1, 'm=application 9 UDP/DTLS/SCTP webrtc-datachannel')
                sdp_lines.insert(last_media_index + 2, 'c=IN IP4 0.0.0.0')
                sdp_lines.insert(last_media_index + 3, 'a=mid:1')
                sdp_lines.insert(last_media_index + 4, 'a=sctp-port:5000')
                sdp_lines.insert(last_media_index + 5, 'a=max-message-size:65536')
                answer = RTCSessionDescription(sdp='\n'.join(sdp_lines), type='answer')
                logger.info(f'Modified answer SDP: {answer.sdp}')
            else:
                logger.info('Data channel already present in answer SDP')

            await pc.setLocalDescription(answer)
            logger.info(f'Local description set for peer {peer_id}')

            # send answer to client
            await websocket.send_json(
                WebRTCSignalingMessage(
                    type=WebRTCSignalingType.ANSWER,
                    sdp=answer.sdp,
                ).model_dump()
            )
            logger.info(f'Answer sent to peer {peer_id}')

        elif message.type == WebRTCSignalingType.CANDIDATE:
            peer = self.webrtc_service.peers.get(peer_id)
            if not peer:
                logger.error(f'No peer found for candidate, peer_id={peer_id}')
                return
            candidate = message.candidate
            if candidate:
                try:
                    rtc_candidate = self._build_rtc_ice_candidate(candidate)
                    logger.info(f'Adding ICE candidate for peer {peer_id}: {rtc_candidate}')
                    await peer.connection.addIceCandidate(rtc_candidate)
                    logger.info(f'ICE candidate added successfully for peer {peer_id}')
                except Exception as e:
                    logger.error(f'Error adding ICE candidate for peer {peer_id}: {e}')
            else:
                logger.warning(
                    f'Received candidate message with no candidate for peer_id={peer_id}'
                )

        else:
            logger.warning(f'Unknown signaling message type: {message.type}')

    def _build_rtc_ice_candidate(self, candidate_obj: WebRTCIceCandidate) -> RTCIceCandidate:
        """
        Build RTCIceCandidate from candidate object, using parse_candidate if candidate is a string.
        """
        if hasattr(candidate_obj, 'candidate') and isinstance(candidate_obj.candidate, str):
            try:
                parts = candidate_obj.candidate.strip().split()
                logger.info(f'Parsing ICE candidate: {candidate_obj.candidate}')
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
            except Exception as e:
                logger.error(f'Error parsing ICE candidate: {e}')
                raise
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
