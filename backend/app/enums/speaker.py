from enum import Enum as PyEnum


class SpeakerType(str, PyEnum):
    user = 'user'
    assistant = 'assistant'
