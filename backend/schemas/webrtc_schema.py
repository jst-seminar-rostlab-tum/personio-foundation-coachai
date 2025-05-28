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
    TRANSCRIPT = 'transcript'


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


class WebRTCIceCandidate(WebRTCSignalingBase):
    """WebRTC ICE candidate signaling message"""

    type: Literal['candidate'] = Field(..., description="Type of the message, must be 'candidate'")
    sdp_mid: str = Field(..., description='Media stream identification')
    sdp_mline_index: int = Field(..., description='Index of the media description in the SDP')
    candidate: str = Field(..., description='ICE candidate string')


class WebRTCSignalingMessage(WebRTCSignalingBase):
    """WebRTC signaling message"""

    sdp: Optional[str] = None
    candidate: Optional[dict] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class WebRTCMessage(WebRTCSignalingMessage):
    """Base class for all WebRTC messages"""

    model_config = ConfigDict(extra='allow')


class WebRTCResponse(BaseModel):
    """Response message for WebRTC signaling"""

    type: Literal['answer'] = Field(..., description="Type of the response, must be 'answer'")
    sdp: str = Field(..., description='Session Description Protocol (SDP) for the answer')


# ============================================================================
#                           BUSINESS LOGIC SCHEMAS
# ============================================================================
# These schemas define the business-specific message formats and data structures
# ============================================================================


class TranscriptMessage(BaseModel):
    """Transcript message format"""

    text: str
    timestamp: str
    confidence: Optional[float] = None
    language: Optional[str] = None


class WebRTCTranscript(WebRTCMessage):
    """WebRTC transcript message"""

    transcript: TranscriptMessage
