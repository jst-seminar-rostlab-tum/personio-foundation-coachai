from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class SkillScores(BaseModel):
    structure: int
    empathy: int
    solution_focus: int
    clarity: int


class TrainingSessionItem(BaseModel):
    session_id: UUID
    title: str
    summary: str
    date: Optional[datetime]
    score: int
    skills: SkillScores


class PaginatedTrainingSessionsResponse(BaseModel):
    page: int
    limit: int
    total_pages: int
    total_sessions: int
    sessions: list[TrainingSessionItem]
