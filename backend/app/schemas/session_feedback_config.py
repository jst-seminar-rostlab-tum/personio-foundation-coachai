"""Pydantic schema definitions for session feedback config."""

from pydantic import RootModel

from app.enums.language import LanguageCode
from app.models.camel_case import CamelModel
from app.schemas.session_feedback import (
    GoalsAchievedRead,
    RecommendationsRead,
    SessionExamplesRead,
)


class SessionFeedbackSystemPromptSet(CamelModel):
    """Schema for session feedback system prompt set."""

    session_examples: str
    goals_achieved: str
    recommendations: str


class SessionFeedbackMockSet(CamelModel):
    """Schema for session feedback mock set."""

    session_examples: SessionExamplesRead
    goals_achieved: GoalsAchievedRead
    recommendations: RecommendationsRead


class SessionFeedbackLanguageSettings(CamelModel):
    """Schema for session feedback language settings."""

    system_prompts: SessionFeedbackSystemPromptSet
    mocks: SessionFeedbackMockSet


class SessionFeedbackConfigRead(RootModel[dict[LanguageCode, SessionFeedbackLanguageSettings]]):
    """Schema for session feedback config read."""

    pass
