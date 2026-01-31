"""Enum definitions for conversation scenario status."""

from enum import Enum as PyEnum


# Enum for status
class ConversationScenarioStatus(str, PyEnum):
    """Enum for conversation scenario status."""

    draft = 'draft'
    ready = 'ready'
    archived = 'archived'
