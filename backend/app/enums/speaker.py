"""Enum definitions for speaker."""

from enum import Enum as PyEnum


class SpeakerType(str, PyEnum):
    """Enum for speaker type."""

    user = 'user'
    assistant = 'assistant'
