from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import event
from sqlalchemy.engine.base import Connection
from sqlalchemy.orm.mapper import Mapper
from sqlmodel import JSON, Column, Field, Relationship

from app.models.camel_case import CamelModel
from app.models.session_feedback import SessionFeedbackMetrics

if TYPE_CHECKING:
    from app.models.conversation_scenario import ConversationScenario
    from app.models.review import Review
    from app.models.session_feedback import SessionFeedback
    from app.models.session_turn import SessionTurn


class SessionStatus(str, Enum):
    started = 'started'
    completed = 'completed'
    failed = 'failed'


class Session(CamelModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    scenario_id: UUID = Field(foreign_key='conversationscenario.id', ondelete='CASCADE')
    scheduled_at: datetime | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None
    ai_persona: dict = Field(default_factory=dict, sa_column=Column(JSON))
    status: SessionStatus = Field(default=SessionStatus.started)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    scenario: 'ConversationScenario' = Relationship(back_populates='sessions')
    session_turns: list['SessionTurn'] = Relationship(back_populates='session', cascade_delete=True)
    feedback: Optional['SessionFeedback'] = Relationship(
        back_populates='session', cascade_delete=True
    )
    session_review: Optional['Review'] = Relationship(back_populates='session', cascade_delete=True)
    # Automatically update `updated_at` before an update


@event.listens_for(Session, 'before_update')
def update_timestamp(mapper: Mapper, connection: Connection, target: 'Session') -> None:
    target.updated_at = datetime.now(UTC)


# Schema for creating a new Session
class SessionCreate(CamelModel):
    scenario_id: UUID
    scheduled_at: datetime | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None
    ai_persona: dict = Field(default_factory=dict, sa_column=Column(JSON))
    status: SessionStatus = Field(default=SessionStatus.started)


class SessionUpdate(CamelModel):
    scenario_id: UUID | None = None
    scheduled_at: datetime | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None
    ai_persona: Optional[dict] = None
    status: Optional[SessionStatus] = None


# Schema for reading Session data
class SessionRead(CamelModel):
    id: UUID
    scenario_id: UUID
    scheduled_at: datetime | None
    started_at: datetime | None
    ended_at: datetime | None
    ai_persona: dict = Field(default_factory=dict, sa_column=Column(JSON))
    status: SessionStatus = Field(default=SessionStatus.started)
    created_at: datetime
    updated_at: datetime


# Schema for reading Session data with details including skill scores, goals achieved,
# session metrics, and feedback insights
class SessionDetailsRead(SessionRead):
    title: str | None = None
    summary: str | None = None
    goals_total: list[str] | None = None
    feedback: Optional['SessionFeedbackMetrics'] = None
    # List of audio file URIs --> located in session_turns
    audio_uris: list[str] = Field(default_factory=list)


SessionDetailsRead.model_rebuild()
