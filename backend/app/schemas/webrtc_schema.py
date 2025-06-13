from enum import Enum

from pydantic import BaseModel, Field

# ============================================================================
#                           WEBRTC ERRORS
# ============================================================================
# These schemas define the error types and classes for WebRTC errors
# ============================================================================


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


class GeminiUserType(Enum):
    """Gemini user types"""

    USER = 'user'
    ASSISTANT = 'assistant'


class WebRTCDataChannelMessage(BaseModel):
    """WebRTC data channel message"""

    role: GeminiUserType = Field(..., description='Role of the message')
    text: str = Field(..., description='Text of the message')


class GeminiSessionState(Enum):
    """Gemini session states"""

    SILENCE = 'silence'
    USER_SPEECH = 'user_speech'
    ASSISTANT_SPEECH = 'assistant_speech'
