from pydantic import RootModel

from app.models.camel_case import CamelModel
from app.models.language import LanguageCode
from app.schemas.session_feedback import (
    GoalsAchievedCollection,
    RecommendationsCollection,
    SessionExamplesCollection,
)


class SessionFeedbackSystemPromptSet(CamelModel):
    session_examples: str
    goals_achieved: str
    recommendations: str


class SessionFeedbackMockSet(CamelModel):
    session_examples: SessionExamplesCollection
    goals_achieved: GoalsAchievedCollection
    recommendations: RecommendationsCollection


class SessionFeedbackLanguageSettings(CamelModel):
    system_prompts: SessionFeedbackSystemPromptSet
    mocks: SessionFeedbackMockSet


class SessionFeedbackConfigRead(RootModel[dict[LanguageCode, SessionFeedbackLanguageSettings]]):
    pass
