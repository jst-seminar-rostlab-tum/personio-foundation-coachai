from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import Field

from app.enums.session_status import SessionStatus
from app.models.camel_case import CamelModel
<<<<<<< HEAD
from app.schemas.session_feedback import SessionFeedbackMetrics
=======
from app.models.session import SessionStatus
from app.schemas.session_feedback import SessionFeedbackRead
>>>>>>> 1dc3d9f07749118303eae86df64f8377fce53210


# Schema for creating a new Session
class SessionCreate(CamelModel):
    scenario_id: UUID
    scheduled_at: datetime | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None
    status: SessionStatus = Field(default=SessionStatus.started)


# Schema for updating an existing Session
class SessionUpdate(CamelModel):
    scenario_id: UUID | None = None
    scheduled_at: datetime | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None
    status: SessionStatus | None = None


# Schema for reading Session data
class SessionRead(CamelModel):
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
    title: str | None = None
    summary: str | None = None
    goals_total: list[str] | None = None
    has_reviewed: bool = False
    feedback: Optional['SessionFeedbackRead'] = None


SessionDetailsRead.model_rebuild()
