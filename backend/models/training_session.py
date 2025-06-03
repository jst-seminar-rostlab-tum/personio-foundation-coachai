from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import event
from sqlalchemy.engine.base import Connection
from sqlalchemy.orm.mapper import Mapper
from sqlmodel import JSON, Column, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from backend.models.conversation_turn import ConversationTurn
    from backend.models.language import Language
    from backend.models.rating import Rating
    from backend.models.training_case import TrainingCase
    from backend.models.training_session_feedback import TrainingSessionFeedback


class TrainingSession(SQLModel, table=True):  # `table=True` makes it a database table
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    case_id: UUID = Field(foreign_key='trainingcase.id')  # Foreign key to TrainingCase
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    language_code: str = Field(foreign_key='language.code')  # Foreign key to LanguageModel
    ai_persona: dict = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

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
    target.updated_at = datetime.now(timezone.utc)


# Schema for creating a new TrainingSession
class TrainingSessionCreate(SQLModel):
    case_id: UUID
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    language_code: str
    ai_persona: dict = Field(default_factory=dict, sa_column=Column(JSON))


# Schema for reading TrainingSession data
class TrainingSessionRead(SQLModel):
    id: UUID
    case_id: UUID
    scheduled_at: Optional[datetime]
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    language_code: str
    ai_persona: dict = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime
    updated_at: datetime
