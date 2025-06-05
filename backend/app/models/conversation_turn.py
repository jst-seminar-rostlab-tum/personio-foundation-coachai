from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.training_session import TrainingSession


class SpeakerEnum(str, Enum):
    user = 'user'
    ai = 'ai'


class ConversationTurn(BaseModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    session_id: UUID = Field(foreign_key='trainingsession.id')  # FK to TrainingSession
    speaker: SpeakerEnum
    start_offset_ms: int
    end_offset_ms: int
    text: str
    audio_uri: str
    ai_emotion: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    session: Optional['TrainingSession'] = Relationship(back_populates='conversation_turns')


# Schema for creating a new ConversationTurn
class ConversationTurnCreate(BaseModel):
    session_id: UUID
    speaker: SpeakerEnum
    start_offset_ms: int
    end_offset_ms: int
    text: str
    audio_uri: str
    ai_emotion: str


# Schema for reading ConversationTurn data
class ConversationTurnRead(BaseModel):
    id: UUID
    session_id: UUID
    speaker: SpeakerEnum
    start_offset_ms: int
    end_offset_ms: int
    text: str
    audio_uri: str
    ai_emotion: str
    created_at: datetime
