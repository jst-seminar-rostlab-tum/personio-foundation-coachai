from pydantic import RootModel

from app.enums.language import LanguageCode
from app.models.camel_case import CamelModel
from app.schemas.session_feedback import (
    GoalsAchievedRead,
    RecommendationsRead,
    SessionExamplesRead,
)


class SessionFeedbackSystemPromptSet(CamelModel):
    session_examples: str
    goals_achieved: str
    recommendations: str


class SessionFeedbackMockSet(CamelModel):
    session_examples: SessionExamplesRead
    goals_achieved: GoalsAchievedRead
    recommendations: RecommendationsRead


class SessionFeedbackLanguageSettings(CamelModel):
    system_prompts: SessionFeedbackSystemPromptSet
    mocks: SessionFeedbackMockSet


class SessionFeedbackConfigRead(RootModel[dict[LanguageCode, SessionFeedbackLanguageSettings]]):
    pass
