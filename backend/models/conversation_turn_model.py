from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import uuid4, UUID
from enum import Enum
from typing import Optional

class SpeakerEnum(str, Enum):
    user = "user"
    ai = "ai"

class ConversationTurnModel(SQLModel, table=True):  # `table=True` makes it a database table
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    session_id: UUID = Field(foreign_key="trainingsessionmodel.id")  # FK to TrainingSessionModel
    speaker: SpeakerEnum
    start_offset_ms: int
    end_offset_ms: int
    text: str
    audio_uri: str
    ai_emotion: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    session: Optional["TrainingSessionModel"] = Relationship(back_populates="conversation_turns")

# Schema for creating a new ConversationTurn
class ConversationTurnCreate(SQLModel):
    session_id: UUID
    speaker: SpeakerEnum
    start_offset_ms: int
    end_offset_ms: int
    text: str
    audio_uri: str
    ai_emotion: str

# Schema for reading ConversationTurn data
class ConversationTurnRead(SQLModel):
    id: UUID
    session_id: UUID
    speaker: SpeakerEnum
    start_offset_ms: int
    end_offset_ms: int
    text: str
    audio_uri: str
    ai_emotion: str
    created_at: datetime