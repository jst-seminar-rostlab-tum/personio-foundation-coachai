from datetime import datetime

from app.models.camel_case import CamelModel
from app.models.language import LanguageCode


# Schema for reading ConversationCategory data
class ConversationCategoryRead(CamelModel):
    id: str  # Changed from UUID to str
    name: str
    default_context: str
    default_goal: str
    default_other_party: str
    is_custom: bool
    language_code: LanguageCode
    created_at: datetime
    updated_at: datetime
