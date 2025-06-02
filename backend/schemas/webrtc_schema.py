from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

# ============================================================================
#                           SIGNALING SCHEMAS
# ============================================================================
# These schemas define the signaling message formats and data structures
# ============================================================================


class WebRTCSignalingType(str, Enum):
    """WebRTC signaling message types"""

    OFFER = 'offer'
    ANSWER = 'answer'
    CANDIDATE = 'candidate'


class WebRTCSignalingBase(BaseModel):
    """Base model for WebRTC signaling messages"""

    type: WebRTCSignalingType = Field(..., description='Type of the signaling message')


class WebRTCOffer(WebRTCSignalingBase):
    """WebRTC offer signaling message"""

    type: Literal['offer'] = Field(..., description="Type of the message, must be 'offer'")
    sdp: str = Field(..., description='Session Description Protocol (SDP) for the offer')


class WebRTCAnswer(WebRTCSignalingBase):
    """WebRTC answer signaling message"""

    type: Literal['answer'] = Field(..., description="Type of the message, must be 'answer'")
    sdp: str = Field(..., description='Session Description Protocol (SDP) for the answer')


class WebRTCIceCandidate(BaseModel):
    """WebRTC ICE candidate"""

    candidate: str = Field(..., description='ICE candidate')
    sdp_mline_index: int = Field(..., description='SDP m-line index', alias='sdpMLineIndex')
    sdp_mid: str = Field(..., description='SDP m-id', alias='sdpMid')


class WebRTCIceCandidateResponse(WebRTCSignalingBase):
    """WebRTC ICE candidate response"""

    type: Literal['candidate'] = Field(..., description="Type of the message, must be 'candidate'")
    candidate: WebRTCIceCandidate = Field(..., description='ICE candidate')


class WebRTCSignalingMessage(WebRTCSignalingBase):
    """WebRTC signaling message"""

    type: WebRTCSignalingType = Field(..., description='Type of the message')
    sdp: Optional[str] = None
    candidate: Optional[WebRTCIceCandidate] = None


class WebRTCMessage(WebRTCSignalingMessage):
    """Base class for all WebRTC messages"""

    model_config = ConfigDict(extra='allow')


class WebSocketErrorType(Enum):
    """WebSocket error types"""

    CONNECTION = 'connection'
    MESSAGE = 'message'
    SIGNALING = 'signaling'
    ICE = 'ice'


# ============================================================================
#                           WEBSOCKET ERRORS
# ============================================================================
# These schemas define the error types and classes for WebSocket errors
# ============================================================================


class WebSocketErrorData(BaseModel):
    """Base WebSocket error data model"""

    message: str = Field(..., description='Error message')
    error_type: WebSocketErrorType = Field(..., description='Error type')
    peer_id: Optional[str] = Field(None, description='Peer ID')


class WebSocketError(Exception):
    """Base WebSocket error class"""

    def __init__(
        self, message: str, error_type: WebSocketErrorType, peer_id: Optional[str] = None
    ) -> None:
        self.error_data = WebSocketErrorData(
            message=message, error_type=error_type, peer_id=peer_id
        )
        super().__init__(message)

    def __str__(self) -> str:
        return (
            f'{self.error_data.error_type.value}: '
            f'{self.error_data.message} (peer_id: {self.error_data.peer_id})'
        )


class WebSocketConnectionError(WebSocketError):
    """Connection related errors"""

    def __init__(self, message: str, peer_id: Optional[str] = None) -> None:
        super().__init__(message, WebSocketErrorType.CONNECTION, peer_id)


class WebSocketMessageError(WebSocketError):
    """Message handling related errors"""

    def __init__(self, message: str, peer_id: Optional[str] = None) -> None:
        super().__init__(message, WebSocketErrorType.MESSAGE, peer_id)


class WebSocketSignalingError(WebSocketError):
    """Signaling related errors"""

    def __init__(self, message: str, peer_id: Optional[str] = None) -> None:
        super().__init__(message, WebSocketErrorType.SIGNALING, peer_id)


class WebSocketIceError(WebSocketError):
    """ICE related errors"""

    def __init__(self, message: str, peer_id: Optional[str] = None) -> None:
        super().__init__(message, WebSocketErrorType.ICE, peer_id)


# ============================================================================
#                           WEBRTC ERRORS
# ============================================================================
# These schemas define the error types and classes for WebRTC errors
# ============================================================================


class WebRTCErrorType(Enum):
    """WebRTC error types"""

    CONNECTION = 'connection'
    DATA_CHANNEL = 'data_channel'
    ICE = 'ice'
    SIGNALING = 'signaling'
    MEDIA = 'media'
    PEER = 'peer'


class WebRTCErrorData(BaseModel):
    """Base WebRTC error data model"""

    message: str = Field(..., description='Error message')
    error_type: WebRTCErrorType = Field(..., description='Error type')
    peer_id: Optional[str] = Field(None, description='Peer ID')


class WebRTCError(Exception):
    """Base WebRTC error class"""

    def __init__(
        self,
        message: str,
        error_type: WebRTCErrorType,
        peer_id: Optional[str] = None,
    ) -> None:
        self.error_data = WebRTCErrorData(message=message, error_type=error_type, peer_id=peer_id)
        super().__init__(message)

    def __str__(self) -> str:
        return (
            f'{self.error_data.error_type.value}: '
            f'{self.error_data.message} (peer_id: {self.error_data.peer_id})'
        )


class WebRTCConnectionError(WebRTCError):
    """Connection related errors"""

    def __init__(self, message: str, peer_id: Optional[str] = None) -> None:
        super().__init__(message, WebRTCErrorType.CONNECTION, peer_id)


class WebRTCDataChannelError(WebRTCError):
    """Data channel related errors"""

    def __init__(self, message: str, peer_id: Optional[str] = None) -> None:
        super().__init__(message, WebRTCErrorType.DATA_CHANNEL, peer_id)


class WebRTCIceError(WebRTCError):
    """ICE related errors"""

    def __init__(self, message: str, peer_id: Optional[str] = None) -> None:
        super().__init__(message, WebRTCErrorType.ICE, peer_id)


class WebRTCSignalingError(WebRTCError):
    """Signaling related errors"""

    def __init__(self, message: str, peer_id: Optional[str] = None) -> None:
        super().__init__(message, WebRTCErrorType.SIGNALING, peer_id)


class WebRTCMediaError(WebRTCError):
    """Media related errors"""

    def __init__(self, message: str, peer_id: Optional[str] = None) -> None:
        super().__init__(message, WebRTCErrorType.MEDIA, peer_id)


class WebRTCPeerError(WebRTCError):
    """Peer related errors"""

    def __init__(self, message: str, peer_id: Optional[str] = None) -> None:
        super().__init__(message, WebRTCErrorType.PEER, peer_id)


# ============================================================================
#                           BUSINESS LOGIC SCHEMAS
# ============================================================================
# These schemas define the business-specific message formats and data structures
# ============================================================================
