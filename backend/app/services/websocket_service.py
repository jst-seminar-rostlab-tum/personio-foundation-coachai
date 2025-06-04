import asyncio
import logging

from aiortc import RTCIceCandidate, RTCSessionDescription
from fastapi import WebSocket

from app.services.webrtc_service import get_webrtc_service

from ..schemas.webrtc_schema import (
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

        try:
            if message.type == WebRTCSignalingType.OFFER:
                # always create/overwrite peer connection, ensure peer is the latest
                try:
                    await self.webrtc_service.create_peer_connection(peer_id)
                except WebRTCError as e:
                    raise WebSocketSignalingError(
                        f'Failed to create peer connection: {str(e)}', peer_id
                    ) from e

                pc = self.webrtc_service.peers[peer_id].connection

                # set remote description
                try:
                    logger.debug(f'Received offer SDP: {message.sdp}')
                    await pc.setRemoteDescription(
                        RTCSessionDescription(sdp=message.sdp, type=WebRTCSignalingType.OFFER)
                    )
                    logger.info(f'Remote description set for peer {peer_id}')
                except Exception as e:
                    raise WebSocketSignalingError(
                        f'Failed to set remote description: {str(e)}', peer_id
                    ) from e

                # Create answer and set local description
                try:
                    answer = await pc.createAnswer()
                    logger.debug(f'Created answer SDP: {answer.sdp}')
                except Exception as e:
                    raise WebSocketSignalingError(
                        f'Failed to create answer: {str(e)}', peer_id
                    ) from e

                # Process SDP and ensure data channel is included
                answer = await self._process_sdp_for_data_channel(answer, message.sdp, peer_id)

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
                            type=WebRTCSignalingType.ANSWER,
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

            elif message.type == WebRTCSignalingType.CANDIDATE:
                peer = self.webrtc_service.peers.get(peer_id)
                if not peer:
                    raise WebSocketSignalingError(
                        f'No peer found for candidate, peer_id={peer_id}', peer_id
                    )

                candidate = message.candidate
                if candidate:
                    try:
                        rtc_candidate = self._build_rtc_ice_candidate(candidate)
                        logger.debug(f'Adding ICE candidate for peer {peer_id}:')
                        logger.debug(f'  - sdpMid: {rtc_candidate.sdpMid}')
                        logger.debug(f'  - sdpMLineIndex: {rtc_candidate.sdpMLineIndex}')
                        logger.debug(f'  - component: {rtc_candidate.component}')
                        logger.debug(f'  - foundation: {rtc_candidate.foundation}')
                        logger.debug(f'  - ip: {rtc_candidate.ip}')
                        logger.debug(f'  - port: {rtc_candidate.port}')
                        logger.debug(f'  - priority: {rtc_candidate.priority}')
                        logger.debug(f'  - protocol: {rtc_candidate.protocol}')
                        logger.debug(f'  - type: {rtc_candidate.type}')

                        await peer.connection.addIceCandidate(rtc_candidate)
                        logger.info(f'ICE candidate added successfully for peer {peer_id}')
                        logger.debug(
                            f'Current ICE connection state: {peer.connection.iceConnectionState}'
                        )
                        logger.debug(f'Current connection state: {peer.connection.connectionState}')
                        logger.debug(f'Current signaling state: {peer.connection.signalingState}')
                    except Exception as e:
                        raise WebSocketIceError(
                            f'Error adding ICE candidate: {str(e)}', peer_id
                        ) from e
                else:
                    logger.debug(
                        f'Received candidate message with no candidate for peer_id={peer_id}'
                    )

            else:
                logger.debug(f'Unknown signaling message type: {message.type}')

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

    async def _process_sdp_for_data_channel(
        self, answer: RTCSessionDescription, offer_sdp: str, peer_id: str
    ) -> RTCSessionDescription:
        """
        Process SDP to ensure data channel is included in the answer.

        Args:
            answer: The answer SDP to process
            offer_sdp: The original offer SDP
            peer_id: The peer ID for logging

        Returns:
            The processed answer SDP with data channel included if necessary
        """
        # Check if data channel is in the offer
        if 'm=application' in offer_sdp:
            logger.debug('Data channel found in offer SDP')
        else:
            logger.debug('Data channel not found in offer SDP')

        # Ensure data channel is included in the answer
        if 'm=application' not in answer.sdp:
            logger.info('Data channel not found in answer SDP, adding it manually')
            try:
                sdp_lines = answer.sdp.split('\n')
                # Add data channel media line after the last media line
                for i, line in enumerate(sdp_lines):
                    if line.startswith('m='):
                        last_media_index = i
                sdp_lines.insert(
                    last_media_index + 1, 'm=application 9 UDP/DTLS/SCTP webrtc-datachannel'
                )
                sdp_lines.insert(last_media_index + 2, 'c=IN IP4 0.0.0.0')
                sdp_lines.insert(last_media_index + 3, 'a=mid:1')
                sdp_lines.insert(last_media_index + 4, 'a=sctp-port:5000')
                sdp_lines.insert(last_media_index + 5, 'a=max-message-size:65536')
                answer = RTCSessionDescription(sdp='\n'.join(sdp_lines), type='answer')
                logger.debug(f'Modified answer SDP: {answer.sdp}')
            except Exception as e:
                raise WebSocketSignalingError(
                    f'Failed to modify answer SDP: {str(e)}', peer_id
                ) from e
        else:
            logger.debug('Data channel already present in answer SDP')

        return answer

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
