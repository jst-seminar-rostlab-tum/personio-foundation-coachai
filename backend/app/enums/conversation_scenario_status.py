from enum import Enum as PyEnum


# Enum for status
class ConversationScenarioStatus(str, PyEnum):
    draft = 'draft'
    ready = 'ready'
    archived = 'archived'
