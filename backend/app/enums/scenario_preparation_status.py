"""Enum definitions for scenario preparation status."""

from enum import Enum as PyEnum


class ScenarioPreparationStatus(str, PyEnum):
    """Enum for scenario preparation status."""

    pending = 'pending'
    completed = 'completed'
    failed = 'failed'
