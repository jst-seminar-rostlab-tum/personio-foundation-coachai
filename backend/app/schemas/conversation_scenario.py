"""Pydantic schema definitions for conversation scenario."""

from datetime import datetime
from uuid import UUID

from app.enums.difficulty_level import DifficultyLevel
from app.enums.language import LanguageCode
from app.models.camel_case import CamelModel
from app.models.conversation_scenario import ConversationScenario
from app.schemas.session_turn import SessionTurnRead


# Schema for creating a new ConversationScenario
class ConversationScenarioCreate(CamelModel):
    """Schema for conversation scenario create."""

    category_id: str | None = None
    custom_category_label: str | None = None
    persona_name: str
    persona: str
    situational_facts: str
    difficulty_level: DifficultyLevel
    language_code: LanguageCode = LanguageCode.en


class ConversationScenarioConfirm(CamelModel):
    """Schema for conversation scenario confirm."""

    message: str
    scenario_id: UUID


class ConversationScenarioRead(CamelModel):
    """Schema for conversation scenario read."""

    scenario: ConversationScenario
    transcript: list[SessionTurnRead]


class ConversationScenarioAIPromptRead(CamelModel):
    """Schema for conversation scenario AI prompt read."""

    category_name: str
    persona: str
    situational_facts: str
    language_code: LanguageCode = LanguageCode.en


class ConversationScenarioSummary(CamelModel):
    """Schema for conversation scenario summary."""

    scenario_id: UUID
    language_code: LanguageCode
    category_name: str
    category_id: str | None = None
    total_sessions: int
    persona_name: str
    difficulty_level: DifficultyLevel
    last_session_at: datetime | None
    average_score: float | None = None


class ConversationScenarioReadDetail(CamelModel):
    """Schema for conversation scenario read detail."""

    scenario_id: UUID
    language_code: LanguageCode
    category_name: str
    category_id: str | None = None
    total_sessions: int
    persona_name: str
    persona: str
    situational_facts: str
    difficulty_level: DifficultyLevel
    last_session_at: datetime | None
    average_score: float | None = None


class PaginatedConversationScenarioSummary(CamelModel):
    """Schema for paginated conversation scenario summary."""

    scenarios: list[ConversationScenarioSummary]
    total_pages: int
    total_scenarios: int
    page: int
    limit: int
