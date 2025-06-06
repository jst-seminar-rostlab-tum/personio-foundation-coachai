from datetime import UTC, datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import event
from sqlalchemy.engine.base import Connection
from sqlalchemy.orm.mapper import Mapper
from sqlmodel import JSON, Column, Field, Relationship, SQLModel

from app.models.training_session_feedback import TrainingSessionFeedbackMetrics

if TYPE_CHECKING:
    from app.models.conversation_turn import ConversationTurn
    from app.models.language import Language
    from app.models.rating import Rating
    from app.models.training_case import TrainingCase
    from app.models.training_session_feedback import TrainingSessionFeedback


class TrainingSession(SQLModel, table=True):  # `table=True` makes it a database table
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    case_id: UUID = Field(foreign_key='trainingcase.id')  # Foreign key to TrainingCase
    scheduled_at: datetime | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None
    language_code: str = Field(foreign_key='language.code')  # Foreign key to LanguageModel
    ai_persona: dict = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

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
class TrainingSessionCreate(SQLModel):
    case_id: UUID
    scheduled_at: datetime | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None
    language_code: str
    ai_persona: dict = Field(default_factory=dict, sa_column=Column(JSON))


# Schema for reading TrainingSession data
class TrainingSessionRead(SQLModel):
    id: UUID
    case_id: UUID
    scheduled_at: datetime | None
    started_at: datetime | None
    ended_at: datetime | None
    language_code: str
    ai_persona: dict = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime
    updated_at: datetime


# Schema for reading TrainingSession data with details including skill scores, goals achieved,
# session metrics, and feedback insights
class TrainingSessionDetailsRead(TrainingSessionRead):
    title: str | None = None
    summary: str | None = None
    feedback: Optional['TrainingSessionFeedbackMetrics'] = None
    # List of audio file URIs --> located in conversation_turns
    audio_uris: list[str] = Field(default_factory=list)


TrainingSessionDetailsRead.model_rebuild()
