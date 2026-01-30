"""Enum definitions for feedback status."""

from enum import Enum as PyEnum


class FeedbackStatus(str, PyEnum):
    """Enum for feedback status."""

    pending = 'pending'
    completed = 'completed'
    failed = 'failed'
