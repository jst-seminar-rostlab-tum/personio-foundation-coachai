from datetime import datetime
from typing import Any, Optional, cast
from uuid import UUID

from sqlalchemy.sql.elements import ColumnElement

from app.models.camel_case import CamelModel
from app.models.conversation_scenario import (
    ConversationScenario,
    ConversationScenarioStatus,
    DifficultyLevel,
)
from app.models.language import LanguageCode

lang_col: ColumnElement[Any] = cast(ColumnElement[Any], ConversationScenario.language_code)
cust_col: ColumnElement[Any] = cast(ColumnElement[Any], ConversationScenario.custom_category_label)


# Schema for creating a new ConversationScenario
class ConversationScenarioCreate(CamelModel):
    category_id: Optional[str] = None
    custom_category_label: Optional[str] = None
    context: str
    goal: str
    other_party: str
    difficulty_level: DifficultyLevel
    tone: Optional[str] = None
    complexity: Optional[str] = None
    language_code: LanguageCode = LanguageCode.en
    status: ConversationScenarioStatus = ConversationScenarioStatus.draft


# Schema for reading ConversationScenario data
class ConversationScenarioRead(CamelModel):
    id: UUID
    user_id: UUID
    category_id: Optional[str]
    custom_category_label: Optional[str]
    context: str
    goal: str
    other_party: str
    difficulty_level: DifficultyLevel
    tone: Optional[str]
    complexity: Optional[str]
    language_code: LanguageCode
    status: ConversationScenarioStatus
    created_at: datetime
    updated_at: datetime


class ConversationScenarioCreateResponse(CamelModel):
    message: str
    scenario_id: UUID


class ConversationScenarioSummary(CamelModel):
    scenario_id: UUID
    language_code: LanguageCode
    category_name: str
    total_sessions: int
    average_score: Optional[float] = None  # None if there are no sessions
