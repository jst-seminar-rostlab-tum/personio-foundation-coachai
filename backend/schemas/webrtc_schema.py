from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field
from aiortc import RTCIceCandidate

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
    CONTROL = 'control'
    CONFIG = 'config'


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



class WebRTCDataChannelConfig(BaseModel):
    """WebRTC data channel configuration"""

    label: str = Field(default='audio', description='Data channel label')
    ordered: bool = Field(default=True, description='Whether the data channel is ordered')
    max_retransmits: int = Field(default=3, description='Maximum number of retransmits', alias='maxRetransmits')
    protocol: str = Field(default='', description='Data channel protocol')
    negotiated: bool = Field(default=False, description='Whether the data channel is negotiated')
    id: Optional[int] = Field(default=None, description='Data channel ID for negotiated channels')


class AudioControlConfig(BaseModel):
    """Audio control configuration"""

    sample_rate: int = Field(default=48000, description='Audio sample rate in Hz', alias='sampleRate')
    silence_threshold: float = Field(default=0.01, description='Silence detection threshold', alias='silenceThreshold')
    silence_duration: float = Field(
        default=0.5, description='Silence duration threshold in seconds', alias='silenceDuration'
    )
    min_speech_duration: float = Field(
        default=0.3, description='Minimum speech duration in seconds', alias='minSpeechDuration'
    )
    buffer_size: int = Field(default=2048, description='Audio buffer size', alias='bufferSize')


class WebRTCControlMessage(WebRTCSignalingBase):
    """WebRTC control message"""

    type: Literal['control'] = Field(..., description="Type of the message, must be 'control'")
    audio_config: AudioControlConfig = Field(..., description='Audio control configuration')


class WebRTCIceCandidateResponse(BaseModel):
    """WebRTC ICE candidate response"""

    status: Literal['success', 'error'] = Field(
        ..., description='Status of the ICE candidate processing'
    )
    message: str = Field(..., description='Response message')


class WebRTCIceCandidate(BaseModel):
    """WebRTC ICE candidate"""

    candidate: str = Field(..., description='ICE candidate')
    sdp_mline_index: int = Field(..., description='SDP m-line index', alias='sdpMLineIndex')
    sdp_mid: str = Field(..., description='SDP m-id', alias='sdpMid')
    username_fragment: Optional[str] = Field(None, description='Username fragment', alias='usernameFragment')

class WebRTCSignalingMessage(WebRTCSignalingBase):
    """WebRTC signaling message"""

    type: WebRTCSignalingType = Field(..., description='Type of the message')
    sdp: Optional[str] = None
    candidate: Optional[WebRTCIceCandidate] = None
    audio_config: Optional[AudioControlConfig] = None
    candidate_response: Optional[WebRTCIceCandidateResponse] = None


class WebRTCMessage(WebRTCSignalingMessage):
    """Base class for all WebRTC messages"""

    model_config = ConfigDict(extra='allow')


class WebRTCResponse(BaseModel):
    """Response message for WebRTC signaling"""

    type: Literal['answer'] = Field(..., description="Type of the response, must be 'answer'")
    sdp: str = Field(..., description='Session Description Protocol (SDP) for the answer')
    audio_config: Optional[AudioControlConfig] = Field(
        None, description='Audio control configuration'
    )


# ============================================================================
#                           BUSINESS LOGIC SCHEMAS
# ============================================================================
# These schemas define the business-specific message formats and data structures
# ============================================================================
