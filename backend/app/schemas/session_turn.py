from datetime import datetime
from uuid import UUID

from app.models.camel_case import CamelModel
from app.models.session_turn import SpeakerEnum


# Schema for creating a new SessionTurn
class SessionTurnCreate(CamelModel):
    session_id: UUID
    speaker: SpeakerEnum
    start_offset_ms: int
    end_offset_ms: int
    text: str
    audio_name: str
    ai_emotion: str


# Schema for reading SessionTurn data
class SessionTurnRead(CamelModel):
    id: UUID
    session_id: UUID
    speaker: SpeakerEnum
    start_offset_ms: int
    end_offset_ms: int
    text: str
    audio_uri: str
    ai_emotion: str
    created_at: datetime
