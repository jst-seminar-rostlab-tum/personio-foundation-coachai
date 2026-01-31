"""Pydantic schema definitions for advisor response."""

from typing import Literal

from app.enums.difficulty_level import DifficultyLevel
from app.models.camel_case import CamelModel


class AdvisorResponse(CamelModel):
    """Schema for advisor response."""

    category_id: Literal[
        'giving_feedback', 'performance_reviews', 'salary_discussions', 'conflict_resolution'
    ]
    persona: str
    persona_name: Literal['angry', 'positive', 'casual', 'shy', 'sad']
    situational_facts: str
    difficulty_level: DifficultyLevel

    mascot_speech: str
