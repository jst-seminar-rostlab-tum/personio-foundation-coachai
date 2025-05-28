from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import event
from sqlalchemy.engine.base import Connection
from sqlalchemy.orm.mapper import Mapper
from sqlmodel import JSON, Column, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from backend.models.training_session import TrainingSession


class FeedbackStatusEnum(str, Enum):
    pending = 'pending'
    completed = 'completed'
    failed = 'failed'


class TrainingSessionFeedback(SQLModel, table=True):  # `table=True` makes it a database table
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    session_id: UUID = Field(foreign_key='trainingsession.id')  # FK to TrainingSession
    scores: dict = Field(default_factory=dict, sa_column=Column(JSON))
    tone_analysis: dict = Field(default_factory=dict, sa_column=Column(JSON))
    overall_score: int
    transcript_uri: str
    speak_time_percent: float
    questions_asked: int
    session_length_s: int
    goals_achieved: int
    examples_positive: Optional[str] = None
    examples_negative: Optional[str] = None
    recommendations: Optional[str] = None
    status: FeedbackStatusEnum = Field(default=FeedbackStatusEnum.pending)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    session: Optional['TrainingSession'] = Relationship(back_populates='feedback')

    # Automatically update `updated_at` before an update


@event.listens_for(TrainingSessionFeedback, 'before_update')
def update_timestamp(
    mapper: Mapper, connection: Connection, target: 'TrainingSessionFeedback'
) -> None:
    target.updated_at = datetime.utcnow()


# Schema for creating a new TrainingSessionFeedback
class TrainingSessionFeedbackCreate(SQLModel):
    session_id: UUID
    scores: dict = Field(default_factory=dict, sa_column=Column(JSON))
    tone_analysis: dict = Field(default_factory=dict, sa_column=Column(JSON))
    overall_score: int
    transcript_uri: str
    speak_time_percent: float
    questions_asked: int
    session_length_s: int
    goals_achieved: int
    examples_positive: Optional[str] = None
    examples_negative: Optional[str] = None
    recommendations: Optional[str] = None
    status: FeedbackStatusEnum = FeedbackStatusEnum.pending


# Schema for reading TrainingSessionFeedback data
class TrainingSessionFeedbackRead(SQLModel):
    id: UUID
    session_id: UUID
    scores: dict = Field(default_factory=dict, sa_column=Column(JSON))
    tone_analysis: dict = Field(default_factory=dict, sa_column=Column(JSON))
    overall_score: int
    transcript_uri: str
    speak_time_percent: float
    questions_asked: int
    session_length_s: int
    goals_achieved: int
    examples_positive: Optional[str] = None
    examples_negative: Optional[str] = None
    recommendations: Optional[str] = None
    status: FeedbackStatusEnum
    created_at: datetime
    updated_at: datetime
