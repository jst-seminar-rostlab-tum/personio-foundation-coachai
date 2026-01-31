"""Enum definitions for preferred learning style."""

from enum import Enum as PyEnum


class PreferredLearningStyle(str, PyEnum):
    """Enum for preferred learning style."""

    visual = 'visual'
    auditory = 'auditory'
    kinesthetic = 'kinesthetic'
