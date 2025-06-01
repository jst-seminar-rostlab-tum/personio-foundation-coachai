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


# ============================================================================
#                           BUSINESS LOGIC SCHEMAS
# ============================================================================
# These schemas define the business-specific message formats and data structures
# ============================================================================
