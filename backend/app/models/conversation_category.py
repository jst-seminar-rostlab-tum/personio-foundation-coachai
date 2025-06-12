from datetime import UTC, datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import event
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Mapper
from sqlmodel import JSON, Column, Field, Relationship

from app.models.camel_case import CamelModel
from app.models.language import LanguageCode

if TYPE_CHECKING:
    from app.models.conversation_scenario import ConversationScenario


class ConversationCategory(CamelModel, table=True):  # `table=True` makes it a database table
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(unique=True)
    icon_uri: str
    system_prompt: str = Field(default='')
    initial_prompt: str = Field(default='')
    ai_setup: dict = Field(default_factory=dict, sa_column=Column(JSON))
    default_context: str = Field(default='')
    default_goal: str = Field(default='')
    default_other_party: str = Field(default='')
    is_custom: bool = Field(default=False)
    language_code: LanguageCode = Field(default=LanguageCode.en)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    conversation_scenarios: list['ConversationScenario'] = Relationship(
        back_populates='category', cascade_delete=True
    )


@event.listens_for(ConversationCategory, 'before_update')
def update_timestamp(
    mapper: Mapper, connection: Connection, target: 'ConversationCategory'
) -> None:
    target.updated_at = datetime.now(UTC)


# Schema for creating a new ConversationCategory
class ConversationCategoryCreate(CamelModel):
    name: Optional[str] = None
    icon_uri: Optional[str] = None
    system_prompt: Optional[str] = None
    initial_prompt: Optional[str] = None
    ai_setup: Optional[dict] = Field(default_factory=dict)
    default_context: Optional[str] = None
    default_goal: Optional[str] = None
    default_other_party: Optional[str] = None
    is_custom: Optional[bool] = None
    language_code: LanguageCode = Field(default=LanguageCode.en)


# Schema for reading ConversationCategory data
class ConversationCategoryRead(CamelModel):
    id: UUID
    name: str
    icon_uri: str
    default_context: str
    default_goal: str
    default_other_party: str
    is_custom: bool
    language_code: LanguageCode
    created_at: datetime
    updated_at: datetime
