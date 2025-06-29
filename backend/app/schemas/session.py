from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import JSON, Column, Field

from app.models.camel_case import CamelModel
from app.models.session import SessionStatus
from app.schemas.session_feedback import SessionFeedbackMetrics


# Schema for creating a new Session
class SessionCreate(CamelModel):
    scenario_id: UUID
    scheduled_at: datetime | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None
    ai_persona: dict = Field(default_factory=dict, sa_column=Column(JSON))
    status: SessionStatus = Field(default=SessionStatus.started)


# Schema for updating an existing Session
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
    allow_admin_access: bool = Field(default=False)
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
