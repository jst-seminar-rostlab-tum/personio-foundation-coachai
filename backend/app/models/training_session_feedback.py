from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import event
from sqlalchemy.engine.base import Connection
from sqlalchemy.orm.mapper import Mapper
from sqlmodel import JSON, Column, Field, Relationship

from app.models.camel_case import CamelModel

if TYPE_CHECKING:
    from app.models.training_session import TrainingSession


class FeedbackStatusEnum(str, Enum):
    pending = 'pending'
    completed = 'completed'
    failed = 'failed'


class PositiveExample(CamelModel):
    heading: str
    feedback: str
    quote: str


class NegativeExample(CamelModel):
    heading: str
    feedback: str
    quote: str
    improved_quote: str


class Recommendation(CamelModel):
    heading: str
    recommendation: str


class TrainingSessionFeedback(CamelModel, table=True):  # `table=True` makes it a database table
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
    example_positive: list[dict] = Field(default_factory=list, sa_column=Column(JSON))
    example_negative: list[dict] = Field(default_factory=list, sa_column=Column(JSON))
    recommendations: list[dict] = Field(default_factory=list, sa_column=Column(JSON))
    status: FeedbackStatusEnum = Field(default=FeedbackStatusEnum.pending)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    session: Optional['TrainingSession'] = Relationship(back_populates='feedback')

    # Automatically update `updated_at` before an update


@event.listens_for(TrainingSessionFeedback, 'before_update')
def update_timestamp(
    mapper: Mapper, connection: Connection, target: 'TrainingSessionFeedback'
) -> None:
    target.updated_at = datetime.now(UTC)


# Schema for creating a new TrainingSessionFeedback
class TrainingSessionFeedbackCreate(CamelModel):
    session_id: UUID
    scores: dict = Field(default_factory=dict, sa_column=Column(JSON))
    tone_analysis: dict = Field(default_factory=dict, sa_column=Column(JSON))
    overall_score: int
    transcript_uri: str
    speak_time_percent: float
    questions_asked: int
    session_length_s: int
    goals_achieved: int
    example_positive: list[PositiveExample] = Field(default_factory=list)
    example_negative: list[NegativeExample] = Field(default_factory=list)
    recommendations: list[Recommendation] = Field(default_factory=list)
    status: FeedbackStatusEnum = FeedbackStatusEnum.pending


# Schema for reading TrainingSessionFeedback data
class TrainingSessionFeedbackRead(CamelModel):
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
    example_positive: list[PositiveExample] = Field(default_factory=list)
    example_negative: list[NegativeExample] = Field(default_factory=list)
    recommendations: list[Recommendation] = Field(default_factory=list)
    status: FeedbackStatusEnum
    created_at: datetime
    updated_at: datetime


# Schema for reading a training session's feedback metrics
class TrainingSessionFeedbackMetrics(CamelModel):
    scores: dict = Field(default_factory=dict, sa_column=Column(JSON))
    tone_analysis: dict = Field(default_factory=dict, sa_column=Column(JSON))
    overall_score: int
    transcript_uri: str
    speak_time_percent: float
    questions_asked: int
    session_length_s: int
    goals_achieved: int
    example_positive: list[PositiveExample] = Field(default_factory=list)
    example_negative: list[NegativeExample] = Field(default_factory=list)
    recommendations: list[Recommendation] = Field(default_factory=list)
