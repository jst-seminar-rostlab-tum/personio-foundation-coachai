from datetime import UTC, datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import event
from sqlalchemy.engine.base import Connection
from sqlalchemy.orm.mapper import Mapper
from sqlmodel import JSON, Column, Field, Relationship

from app.models.camel_case import CamelModel

if TYPE_CHECKING:
    from app.models.session import Session

from app.enums.feedback_status import FeedbackStatus


class SessionFeedback(CamelModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    session_id: UUID = Field(foreign_key='session.id', ondelete='CASCADE')
    scores: dict = Field(default_factory=dict, sa_column=Column(JSON))
    tone_analysis: dict = Field(default_factory=dict, sa_column=Column(JSON))
    overall_score: float
    transcript_uri: str
    full_audio_filename: str
    document_names: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    speak_time_percent: float
    questions_asked: int
    session_length_s: int
    goals_achieved: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    example_positive: list[dict] = Field(default_factory=list, sa_column=Column(JSON))
    example_negative: list[dict] = Field(default_factory=list, sa_column=Column(JSON))
    recommendations: list[dict] = Field(default_factory=list, sa_column=Column(JSON))
    status: FeedbackStatus = Field(default=FeedbackStatus.pending)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    session: Optional['Session'] = Relationship(back_populates='feedback')


@event.listens_for(SessionFeedback, 'before_update')
def update_timestamp(mapper: Mapper, connection: Connection, target: 'SessionFeedback') -> None:
    target.updated_at = datetime.now(UTC)
