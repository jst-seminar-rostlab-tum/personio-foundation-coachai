"""Enum definitions for session status."""

from enum import Enum as PyEnum


class SessionStatus(str, PyEnum):
    """Enum for session status."""

    started = 'started'
    completed = 'completed'
    failed = 'failed'
