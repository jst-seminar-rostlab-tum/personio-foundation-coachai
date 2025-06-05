from datetime import datetime
from uuid import UUID

from app.models.base import BaseModel, Field


class SkillScores(BaseModel):
    structure: int
    empathy: int
    solution_focus: int = Field(alias='solutionFocus')
    clarity: int


class TrainingSessionItem(BaseModel):
    session_id: UUID = Field(alias='sessionId')
    title: str
    summary: str
    date: datetime | None
    score: int
    skills: SkillScores


class PaginatedTrainingSessionsResponse(BaseModel):
    page: int
    limit: int
    total_pages: int = Field(alias='totalPages')
    total_sessions: int = Field(alias='totalSessions')
    sessions: list[TrainingSessionItem]
