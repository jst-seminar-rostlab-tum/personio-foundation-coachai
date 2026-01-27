"""Pydantic schema definitions for conversation category."""

from datetime import datetime

from app.enums.language import LanguageCode
from app.models.camel_case import CamelModel


# Schema for reading ConversationCategory data
class ConversationCategoryRead(CamelModel):
    """Schema for conversation category read."""

    id: str
    name: str
    is_custom: bool
    language_code: LanguageCode
    created_at: datetime
    updated_at: datetime
