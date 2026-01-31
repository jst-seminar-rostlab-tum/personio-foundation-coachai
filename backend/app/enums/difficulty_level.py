"""Enum definitions for difficulty level."""

from enum import Enum as PyEnum


class DifficultyLevel(str, PyEnum):
    """Enum for difficulty level."""

    easy = 'easy'
    medium = 'medium'
    hard = 'hard'
