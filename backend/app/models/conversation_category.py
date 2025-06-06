from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import event
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Mapper
from sqlmodel import JSON, Column, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.training_case import TrainingCase


class ConversationCategory(SQLModel, table=True):  # `table=True` makes it a database table
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
    language_code: str = Field(foreign_key='language.code')  # FK to Language model
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    training_cases: list['TrainingCase'] = Relationship(
        back_populates='category', cascade_delete=True
    )


@event.listens_for(ConversationCategory, 'before_update')
def update_timestamp(
    mapper: Mapper, connection: Connection, target: 'ConversationCategory'
) -> None:
    target.updated_at = datetime.now(UTC)


# Schema for creating a new ConversationCategory
class ConversationCategoryCreate(SQLModel):
    name: str | None = None
    icon_uri: str | None = None
    system_prompt: str | None = None
    initial_prompt: str | None = None
    ai_setup: dict | None = Field(default_factory=dict)
    default_context: str | None = None
    default_goal: str | None = None
    default_other_party: str | None = None
    is_custom: bool | None = None
    language_code: str | None = None


# Schema for reading ConversationCategory data
class ConversationCategoryRead(SQLModel):
    id: UUID
    name: str
    icon_uri: str
    default_context: str
    default_goal: str
    default_other_party: str
    is_custom: bool
    language_code: str
    created_at: datetime
    updated_at: datetime
