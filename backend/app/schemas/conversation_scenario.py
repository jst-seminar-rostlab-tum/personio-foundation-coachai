from typing import Optional
from uuid import UUID

from app.models.camel_case import CamelModel
from app.models.conversation_scenario import ConversationScenarioStatus, DifficultyLevel
from app.models.language import LanguageCode


# Schema for creating a new ConversationScenario
class ConversationScenarioCreate(CamelModel):
    category_id: Optional[str] = None
    custom_category_label: Optional[str] = None
    persona: str
    situational_facts: str
    difficulty_level: DifficultyLevel
    language_code: LanguageCode = LanguageCode.en
    status: ConversationScenarioStatus = ConversationScenarioStatus.draft


class ConversationScenarioCreateResponse(CamelModel):
    message: str
    scenario_id: UUID
