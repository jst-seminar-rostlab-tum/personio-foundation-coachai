from datetime import datetime
from uuid import UUID

from app.models.camel_case import CamelModel
from app.models.session import SessionStatus


class SkillScores(CamelModel):
    structure: int
    empathy: int
    focus: int
    clarity: int


class SessionItem(CamelModel):
    session_id: UUID
    title: str
    summary: str
    date: datetime | None
    score: int
    skills: SkillScores
    status: SessionStatus
    allow_admin_access: bool = False


class PaginatedSessionsResponse(CamelModel):
    page: int
    limit: int
    total_pages: int
    total_sessions: int
    sessions: list[SessionItem]
