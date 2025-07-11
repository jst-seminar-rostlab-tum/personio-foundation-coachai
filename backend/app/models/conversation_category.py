from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import event
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Mapper
from sqlmodel import Field, Relationship

from app.models.camel_case import CamelModel
from app.models.language import LanguageCode

if TYPE_CHECKING:
    from app.models.conversation_scenario import ConversationScenario


class ConversationCategory(CamelModel, table=True):
    id: str = Field(primary_key=True)
    name: str = Field(unique=True)
    initial_prompt: str = Field(default='')
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
