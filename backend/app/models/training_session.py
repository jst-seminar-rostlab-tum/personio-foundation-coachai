from datetime import UTC, datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import JSON, Column, event
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Mapper
from sqlmodel import Field, Relationship, SQLModel

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.conversation_turn import ConversationTurn
    from app.models.language import Language
    from app.models.rating import Rating
    from app.models.training_case import TrainingCase
    from app.models.training_session_feedback import TrainingSessionFeedback


class TrainingSession(SQLModel, table=True):  # `table=True` makes it a database table
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    case_id: UUID = Field(foreign_key='trainingcase.id', alias='caseId')  # Foreign key
    scheduled_at: Optional[datetime] = Field(default=None, alias='scheduledAt')
    started_at: Optional[datetime] = Field(default=None, alias='startedAt')
    ended_at: Optional[datetime] = Field(default=None, alias='endedAt')
    language_code: str = Field(foreign_key='language.code', alias='languageCode')
    ai_persona: dict = Field(default_factory=dict, sa_column=Column(JSON), alias='aiPersona')
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), alias='createdAt')
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), alias='updatedAt')

    # Relationships
    case: Optional['TrainingCase'] = Relationship(back_populates='sessions')
    language: Optional['Language'] = Relationship()  # Relationship to Language
    conversation_turns: list['ConversationTurn'] = Relationship(
        back_populates='session', cascade_delete=True
    )
    feedback: Optional['TrainingSessionFeedback'] = Relationship(
        back_populates='session', cascade_delete=True
    )
    ratings: list['Rating'] = Relationship(back_populates='session', cascade_delete=True)


# Automatically update `updated_at` before an update
@event.listens_for(TrainingSession, 'before_update')
def update_timestamp(mapper: Mapper, connection: Connection, target: 'TrainingSession') -> None:
    target.updated_at = datetime.now(UTC)


# Schema for creating a new TrainingSession
class TrainingSessionCreate(BaseModel):
    case_id: UUID
    scheduled_at: Optional[datetime]
    language_code: str
    ai_persona: dict


# Schema for reading TrainingSession data
class TrainingSessionRead(BaseModel):
    id: UUID
    case_id: UUID
    scheduled_at: Optional[datetime]
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    language_code: str
    ai_persona: dict
    created_at: datetime
    updated_at: datetime
