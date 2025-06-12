"""
WebRTC Event System

This module defines event types and data structures for WebRTC service events,
similar to the local audio stream event system.

Event types include:
- WebRTCAudioEventType: Audio stream events (start/end, voice activity, silence, quality)
- WebRTCSessionEventType: Session lifecycle events (start/end, Gemini connection, errors)
- WebRTCDataChannelEventType: Data channel events (ready/closed, transcript, messages)
- WebRTCUserEventType: User interaction events (messages sent/received)
"""

import time
from dataclasses import dataclass
from enum import Enum
from typing import Generic, TypeVar

T = TypeVar('T')


class WebRTCAudioEventType(Enum):
    """WebRTC audio event types"""

    AUDIO_STREAM_START = 'audio_stream_start'
    AUDIO_STREAM_END = 'audio_stream_end'
    VOICE_ACTIVITY_DETECTED = 'voice_activity_detected'
    SILENCE_DETECTED = 'silence_detected'
    AUDIO_QUALITY_CHANGED = 'audio_quality_changed'
    AUDIO_CHUNK_READY = 'audio_chunk_ready'


class WebRTCSessionEventType(Enum):
    """WebRTC session event types"""

    SESSION_STARTED = 'session_started'
    SESSION_ENDED = 'session_ended'
    SESSION_ERROR = 'session_error'
    GEMINI_CONNECTED = 'gemini_connected'
    GEMINI_DISCONNECTED = 'gemini_disconnected'


class WebRTCDataChannelEventType(Enum):
    """WebRTC data channel event types"""

    CHANNEL_READY = 'channel_ready'
    CHANNEL_CLOSED = 'channel_closed'
    TRANSCRIPT_SENT = 'transcript_sent'
    MESSAGE_RECEIVED = 'message_received'


class WebRTCUserEventType(Enum):
    """WebRTC user event types"""

    USER_MESSAGE_SENT = 'user_message_sent'
    ASSISTANT_MESSAGE_RECEIVED = 'assistant_message_received'
    SEND_REALTIME_INPUT = 'send_realtime_input'


@dataclass
class WebRTCAudioEvent(Generic[T]):
    """WebRTC audio event"""

    type: WebRTCAudioEventType
    peer_id: str
    data: T | None = None
    timestamp: float | None = None

    def __post_init__(self) -> None:
        if self.timestamp is None:
            self.timestamp = time.time()


@dataclass
class WebRTCSessionEvent(Generic[T]):
    """WebRTC session event"""

    type: WebRTCSessionEventType
    peer_id: str
    data: T | None = None
    timestamp: float | None = None

    def __post_init__(self) -> None:
        if self.timestamp is None:
            self.timestamp = time.time()


@dataclass
class WebRTCDataChannelEvent(Generic[T]):
    """WebRTC data channel event"""

    type: WebRTCDataChannelEventType
    peer_id: str
    data: T | None = None
    timestamp: float | None = None

    def __post_init__(self) -> None:
        if self.timestamp is None:
            self.timestamp = time.time()


@dataclass
class WebRTCUserEvent(Generic[T]):
    """WebRTC user event"""

    type: WebRTCUserEventType
    peer_id: str
    data: T | None = None
    timestamp: float | None = None

    def __post_init__(self) -> None:
        if self.timestamp is None:
            self.timestamp = time.time()
