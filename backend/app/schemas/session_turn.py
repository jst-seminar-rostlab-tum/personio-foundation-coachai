from datetime import datetime
from typing import Optional
from uuid import UUID

from app.enums.speaker import SpeakerType
from app.models.camel_case import CamelModel


# Schema for creating a new SessionTurn
class SessionTurnCreate(CamelModel):
    session_id: UUID
    speaker: SpeakerType
    start_offset_ms: int
    end_offset_ms: int
    text: str


# Schema for reading SessionTurn data
class SessionTurnRead(CamelModel):
    id: UUID
    speaker: SpeakerType
    full_audio_start_offset_ms: int
    text: str
    ai_emotion: Optional[str] = None
    created_at: datetime
