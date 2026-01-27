"""Enum definitions for experience."""

from enum import Enum as PyEnum


class Experience(str, PyEnum):
    """Enum for experience."""

    beginner = 'beginner'
    intermediate = 'intermediate'
    skilled = 'skilled'
    advanced = 'advanced'
    expert = 'expert'
