import asyncio
import logging
import re

from aiortc import RTCIceCandidate, RTCSessionDescription
from fastapi import WebSocket

from app.schemas.webrtc_schema import (
    WebRTCError,
    WebRTCIceCandidate,
    WebRTCSignalingMessage,
    WebRTCSignalingType,
    WebSocketConnectionError,
    WebSocketError,
    WebSocketErrorType,
    WebSocketIceError,
    WebSocketSignalingError,
)
from app.services.audio_processor import SEND_SAMPLE_RATE
from app.services.webrtc_service import get_webrtc_service

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

    def _modify_sdp_for_opus(self, sdp: str) -> str:
        """Modify SDP for opus encoding"""
        found = re.findall(r'a=rtpmap:(\d+) opus/(\d+)/2', sdp)
        if found:
            payload_type, sample_rate = found[0]
            sdp = sdp.replace(f'opus/{sample_rate}/2', 'opus/16000/2')
            sdp = sdp.replace(
                'opus/16000/2\r\n',
                'opus/16000/2\r\n'
                + f'a=fmtp:{payload_type} useinbandfec=1;u'
                + f'sedtx=1;maxaveragebitrate={SEND_SAMPLE_RATE}\r\n',
            )
            logger.info(
                f'Modified SDP with opus parameters: sample_rate=16000, bitrate={SEND_SAMPLE_RATE}'
            )
        return sdp

    async def handle_webrtc_message(
        self,
        websocket: WebSocket,
        message: WebRTCSignalingMessage,
    ) -> None:
        """Handle WebRTC signaling messages"""
        peer_id = str(id(websocket))

        try:
            if message.signal_type == WebRTCSignalingType.OFFER:
                # always create/overwrite peer connection, ensure peer is the latest
                try:
                    await self.webrtc_service.create_peer_connection(peer_id)
                except WebRTCError as e:
                    raise WebSocketSignalingError(
                        f'Failed to create peer connection: {str(e)}', peer_id
                    ) from e

                pc = self.webrtc_service.peer_session_manager.get_peer(peer_id).connection

                # modify offer SDP
                modified_sdp = self._modify_sdp_for_opus(message.sdp)
                logger.debug(f'Modified offer SDP: {modified_sdp}')

                # set remote description
                try:
                    await pc.setRemoteDescription(
                        RTCSessionDescription(sdp=modified_sdp, type=WebRTCSignalingType.OFFER)
                    )
                    logger.info(f'Remote description set for peer {peer_id}')
                except Exception as e:
                    raise WebSocketSignalingError(
                        f'Failed to set remote description: {str(e)}', peer_id
                    ) from e

                # Create answer and set local description
                try:
                    answer = await pc.createAnswer()
                    # modify answer SDP
                    answer.sdp = self._modify_sdp_for_opus(answer.sdp)
                    logger.debug(f'Created and modified answer SDP: {answer.sdp}')
                except Exception as e:
                    raise WebSocketSignalingError(
                        f'Failed to create answer: {str(e)}', peer_id
                    ) from e

                # Set local description BEFORE sending answer
                try:
                    await pc.setLocalDescription(answer)
                    logger.info(f'Local description set for peer {peer_id}')
                except Exception as e:
                    raise WebSocketSignalingError(
                        f'Failed to set local description: {str(e)}', peer_id
                    ) from e

                # send answer to client
                try:
                    await websocket.send_json(
                        WebRTCSignalingMessage(
                            signal_type=WebRTCSignalingType.ANSWER,
                            sdp=answer.sdp,
                        ).model_dump()
                    )
                    logger.info(f'Answer sent to peer {peer_id}')
                except Exception as e:
                    raise WebSocketConnectionError(
                        f'Failed to send answer: {str(e)}', peer_id
                    ) from e

                # Wait for ICE gathering to complete
                if pc.iceGatheringState != 'complete':
                    logger.debug(f'Waiting for ICE gathering to complete for peer {peer_id}')
                    try:
                        while pc.iceGatheringState != 'complete':
                            await asyncio.sleep(0.1)
                        logger.info(f'ICE gathering completed for peer {peer_id}')
                    except Exception as e:
                        raise WebSocketIceError(
                            f'Error waiting for ICE gathering: {str(e)}', peer_id
                        ) from e

            elif message.signal_type == WebRTCSignalingType.CANDIDATE:
                peer = self.webrtc_service.peer_session_manager.get_peer(peer_id)
                if not peer:
                    raise WebSocketSignalingError(
                        f'No peer found for candidate, peer_id={peer_id}', peer_id
                    )

                candidate = message.candidate
                if candidate:
                    try:
                        rtc_candidate = self._build_rtc_ice_candidate(candidate)

                        await peer.connection.addIceCandidate(rtc_candidate)
                        logger.info(f'ICE candidate added successfully for peer {peer_id}')
                    except Exception as e:
                        raise WebSocketIceError(
                            f'Error adding ICE candidate: {str(e)}', peer_id
                        ) from e
                else:
                    logger.debug(
                        f'Received candidate message with no candidate for peer_id={peer_id}'
                    )

            else:
                logger.debug(f'Unknown signaling message type: {message.signal_type}')

        except WebSocketError:
            raise
        except WebRTCError as e:
            raise WebSocketError(
                f'WebRTC error: {str(e)}', WebSocketErrorType.SIGNALING, peer_id
            ) from e
        except Exception as e:
            raise WebSocketError(
                f'Unexpected error: {str(e)}', WebSocketErrorType.MESSAGE, peer_id
            ) from e

    def _build_rtc_ice_candidate(self, candidate_obj: WebRTCIceCandidate) -> RTCIceCandidate:
        """
        Build RTCIceCandidate from candidate object.
        """
        if not candidate_obj.candidate:
            raise WebSocketIceError('Candidate string is empty')

        try:
            # Parse the candidate string
            parts = candidate_obj.candidate.strip().split()
            if not parts[0].startswith('candidate:'):
                raise WebSocketIceError('Invalid candidate string format')

            # Extract components
            foundation = parts[0][len('candidate:') :]
            component = int(parts[1])
            protocol = parts[2].lower()
            priority = int(parts[3])
            ip = parts[4]
            port = int(parts[5])
            type_ = parts[7]

            logger.debug('Parsed ICE candidate components:')
            logger.debug(f'  - foundation: {foundation}')
            logger.debug(f'  - component: {component}')
            logger.debug(f'  - protocol: {protocol}')
            logger.debug(f'  - priority: {priority}')
            logger.debug(f'  - ip: {ip}')
            logger.debug(f'  - port: {port}')
            logger.debug(f'  - type: {type_}')

            return RTCIceCandidate(
                sdpMid=candidate_obj.sdp_mid,
                sdpMLineIndex=candidate_obj.sdp_mline_index,
                component=component,
                foundation=foundation,
                ip=ip,
                port=port,
                priority=priority,
                protocol=protocol,
                type=type_,
            )
        except WebSocketIceError:
            raise
        except Exception as e:
            raise WebSocketIceError(f'Error parsing ICE candidate: {str(e)}') from e


def get_websocket_service() -> WebSocketService:
    """
    Get WebSocket service instance

    Returns:
        WebSocketService: Global instance of WebSocket service
    """
    if not hasattr(get_websocket_service, '_instance'):
        get_websocket_service._instance = WebSocketService()
    return get_websocket_service._instance
