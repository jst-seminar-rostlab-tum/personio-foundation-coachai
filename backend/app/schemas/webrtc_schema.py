from enum import Enum
from typing import Literal

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

    signal_type: WebRTCSignalingType = Field(..., description='Type of the signaling message')


class WebRTCOffer(WebRTCSignalingBase):
    """WebRTC offer signaling message"""

    signal_type: Literal['offer'] = Field(..., description="Type of the message, must be 'offer'")
    sdp: str = Field(..., description='Session Description Protocol (SDP) for the offer')


class WebRTCAnswer(WebRTCSignalingBase):
    """WebRTC answer signaling message"""

    signal_type: Literal['answer'] = Field(..., description="Type of the message, must be 'answer'")
    sdp: str = Field(..., description='Session Description Protocol (SDP) for the answer')


class WebRTCIceCandidate(BaseModel):
    """WebRTC ICE candidate"""

    candidate: str = Field(..., description='ICE candidate')
    sdp_mline_index: int = Field(..., description='SDP m-line index', alias='sdpMLineIndex')
    sdp_mid: str = Field(..., description='SDP m-id', alias='sdpMid')


class WebRTCSignalingMessage(WebRTCSignalingBase):
    """WebRTC signaling message"""

    signal_type: WebRTCSignalingType = Field(..., description='Type of the message')
    sdp: str | None = None
    candidate: WebRTCIceCandidate | None = None


class WebRTCMessage(WebRTCSignalingMessage):
    """Base class for all WebRTC messages"""

    model_config = ConfigDict(extra='allow')


# ============================================================================
#                           WEBSOCKET ERRORS
# ============================================================================
# These schemas define the error types and classes for WebSocket errors
# ============================================================================


class WebSocketErrorType(Enum):
    """WebSocket error types"""

    CONNECTION = 'connection'
    MESSAGE = 'message'
    SIGNALING = 'signaling'
    ICE = 'ice'


class WebSocketErrorData(BaseModel):
    """Base WebSocket error data model"""

    message: str = Field(..., description='Error message')
    error_type: WebSocketErrorType = Field(..., description='Error type')
    peer_id: str | None = Field(None, description='Peer ID')


class WebSocketError(Exception):
    """Base WebSocket error class"""

    def __init__(
        self, message: str, error_type: WebSocketErrorType, peer_id: str | None = None
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

    def __init__(self, message: str, peer_id: str | None = None) -> None:
        super().__init__(message, WebSocketErrorType.CONNECTION, peer_id)


class WebSocketMessageError(WebSocketError):
    """Message handling related errors"""

    def __init__(self, message: str, peer_id: str | None = None) -> None:
        super().__init__(message, WebSocketErrorType.MESSAGE, peer_id)


class WebSocketSignalingError(WebSocketError):
    """Signaling related errors"""

    def __init__(self, message: str, peer_id: str | None = None) -> None:
        super().__init__(message, WebSocketErrorType.SIGNALING, peer_id)


class WebSocketIceError(WebSocketError):
    """ICE related errors"""

    def __init__(self, message: str, peer_id: str | None = None) -> None:
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
    peer_id: str | None = Field(None, description='Peer ID')


class WebRTCError(Exception):
    """Base WebRTC error class"""

    def __init__(
        self,
        message: str,
        error_type: WebRTCErrorType,
        peer_id: str | None = None,
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

    def __init__(self, message: str, peer_id: str | None = None) -> None:
        super().__init__(message, WebRTCErrorType.CONNECTION, peer_id)


class WebRTCDataChannelError(WebRTCError):
    """Data channel related errors"""

    def __init__(self, message: str, peer_id: str | None = None) -> None:
        super().__init__(message, WebRTCErrorType.DATA_CHANNEL, peer_id)


class WebRTCIceError(WebRTCError):
    """ICE related errors"""

    def __init__(self, message: str, peer_id: str | None = None) -> None:
        super().__init__(message, WebRTCErrorType.ICE, peer_id)


class WebRTCSignalingError(WebRTCError):
    """Signaling related errors"""

    def __init__(self, message: str, peer_id: str | None = None) -> None:
        super().__init__(message, WebRTCErrorType.SIGNALING, peer_id)


class WebRTCMediaError(WebRTCError):
    """Media related errors"""

    def __init__(self, message: str, peer_id: str | None = None) -> None:
        super().__init__(message, WebRTCErrorType.MEDIA, peer_id)


class WebRTCPeerError(WebRTCError):
    """Peer related errors"""

    def __init__(self, message: str, peer_id: str | None = None) -> None:
        super().__init__(message, WebRTCErrorType.PEER, peer_id)


# ============================================================================
#                           GEMINI SCHEMAS
# ============================================================================
# These schemas define the schemas for Gemini
# ============================================================================


class GeminiStreamErrorType(Enum):
    """Gemini stream error types"""

    AUTH = 'authentication'
    CONNECTION = 'connection'
    SEND = 'send'
    RECEIVE = 'receive'


class GeminiStreamErrorData(BaseModel):
    """Gemini stream error data"""

    message: str = Field(..., description='Error message')
    error_type: GeminiStreamErrorType = Field(..., description='Error type')
    peer_id: str | None = Field(None, description='Peer ID')


class GeminiStreamError(Exception):
    """Gemini stream error"""

    def __init__(
        self, message: str, error_type: GeminiStreamErrorType, peer_id: str | None = None
    ) -> None:
        self.error_data = GeminiStreamErrorData(
            message=message, error_type=error_type, peer_id=peer_id
        )
        super().__init__(message)


class GeminiStreamAuthenticationError(GeminiStreamError):
    """Gemini stream authentication error"""

    def __init__(self, message: str, peer_id: str | None = None) -> None:
        super().__init__(message, GeminiStreamErrorType.AUTH, peer_id)


class GeminiStreamConnectionError(GeminiStreamError):
    """Gemini stream connection error"""

    def __init__(self, message: str, peer_id: str | None = None) -> None:
        super().__init__(message, GeminiStreamErrorType.CONNECTION, peer_id)


class GeminiStreamSendError(GeminiStreamError):
    """Gemini stream send error"""

    def __init__(self, message: str, peer_id: str | None = None) -> None:
        super().__init__(message, GeminiStreamErrorType.SEND, peer_id)


class GeminiStreamReceiveError(GeminiStreamError):
    """Gemini stream receive error"""

    def __init__(self, message: str, peer_id: str | None = None) -> None:
        super().__init__(message, GeminiStreamErrorType.RECEIVE, peer_id)


# ============================================================================
#                           BUSINESS LOGIC SCHEMAS
# ============================================================================
# These schemas define the business-specific message formats and data structures
# ============================================================================


GEMINI_SAMPLE_RATE = 16000  # Default sample rate for Gemini


class GeminiAudioChunk(BaseModel):
    """Gemini audio chunk"""

    data: bytes = Field(..., description='Audio chunk data')
    timestamp: float = Field(..., description='Audio chunk timestamp')
    sample_rate: int = Field(
        default=GEMINI_SAMPLE_RATE, description='Audio chunk sample rate'
    )  # 16kHz is standard for voice


class GeminiAudioResponse(BaseModel):
    audio_data: bytes | None = Field(None, description='Audio data')
    transcript: str | None = Field(None, description='Text data')
    is_final: bool = Field(False, description='Whether this is the final response')
