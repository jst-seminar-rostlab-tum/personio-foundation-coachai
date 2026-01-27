"""Pydantic schema definitions for sessions paginated."""

from datetime import datetime
from uuid import UUID

from app.enums.session_status import SessionStatus
from app.models.camel_case import CamelModel


class SkillScores(CamelModel):
    """Schema for skill scores."""

    structure: int
    empathy: int
    focus: int
    clarity: int


class SessionItem(CamelModel):
    """Schema for session item."""

    session_id: UUID
    title: str
    summary: str
    date: datetime | None
    overall_score: float
    skills: SkillScores
    status: SessionStatus
    session_length_s: int = 0
    allow_admin_access: bool = False


class PaginatedSessionRead(CamelModel):
    """Schema for paginated session read."""

    page: int
    limit: int
    total_pages: int
    total_sessions: int
    sessions: list[SessionItem]
