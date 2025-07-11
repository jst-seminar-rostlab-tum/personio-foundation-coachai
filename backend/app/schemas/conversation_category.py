from datetime import datetime

from app.models.camel_case import CamelModel
from app.models.language import LanguageCode


# Schema for reading ConversationCategory data
class ConversationCategoryRead(CamelModel):
    id: str
    name: str
    is_custom: bool
    language_code: LanguageCode
    created_at: datetime
    updated_at: datetime
