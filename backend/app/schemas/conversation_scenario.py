from uuid import UUID

from app.enums.difficulty_level import DifficultyLevel
from app.enums.language import LanguageCode
from app.models.camel_case import CamelModel
from app.models.conversation_scenario import ConversationScenario
from app.schemas.session_turn import SessionTurnRead


# Schema for creating a new ConversationScenario
class ConversationScenarioCreate(CamelModel):
    category_id: str | None = None
    custom_category_label: str | None = None
    persona_name: str
    persona: str
    situational_facts: str
    difficulty_level: DifficultyLevel
    language_code: LanguageCode = LanguageCode.en


class ConversationScenarioConfirm(CamelModel):
    message: str
    scenario_id: UUID


class ConversationScenarioRead(CamelModel):
    scenario: ConversationScenario
    transcript: list[SessionTurnRead]


class ConversationScenarioAIPromptRead(CamelModel):
    category_name: str
    persona: str
    situational_facts: str
    language_code: LanguageCode = LanguageCode.en


class ConversationScenarioSummary(CamelModel):
    scenario_id: UUID
    language_code: LanguageCode
    category_name: str
    total_sessions: int
    average_score: float | None = None  # None if there are no sessions
