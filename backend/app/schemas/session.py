"""Pydantic schema definitions for session."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import Field

from app.enums.session_status import SessionStatus
from app.models.camel_case import CamelModel
from app.schemas.session_feedback import SessionFeedbackRead


# Schema for creating a new Session
class SessionCreate(CamelModel):
    """Schema for session create."""

    scenario_id: UUID
    scheduled_at: datetime | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None
    status: SessionStatus = Field(default=SessionStatus.started)


# Schema for updating an existing Session
class SessionUpdate(CamelModel):
    """Schema for session update."""

    scenario_id: UUID | None = None
    scheduled_at: datetime | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None
    status: SessionStatus | None = None


# Schema for reading Session data
class SessionRead(CamelModel):
    """Schema for session read."""

    id: UUID
    scenario_id: UUID
    scheduled_at: datetime | None
    started_at: datetime | None
    ended_at: datetime | None
    status: SessionStatus = Field(default=SessionStatus.started)
    allow_admin_access: bool = Field(default=False)
    created_at: datetime
    updated_at: datetime


# Schema for reading Session data with details including skill scores, goals achieved,
# session metrics, and feedback insights
class SessionDetailsRead(SessionRead):
    """Schema for session details read."""

    title: str | None = None
    goals_total: list[str] | None = None
    has_reviewed: bool = False
    feedback: Optional['SessionFeedbackRead'] = None


SessionDetailsRead.model_rebuild()
