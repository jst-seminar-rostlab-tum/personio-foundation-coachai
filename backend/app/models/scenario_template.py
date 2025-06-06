from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import event
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Mapper
from sqlmodel import JSON, Column, Field, Relationship

from app.models.camel_case import CamelModel

if TYPE_CHECKING:
    from app.models.conversation_category import ConversationCategory
    from app.models.language import Language
    from app.models.training_case import TrainingCase


class ScenarioTemplateStatus(str, Enum):
    draft = 'draft'
    ready = 'ready'
    archived = 'archived'


class ScenarioTemplate(CamelModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    category_id: Optional[UUID] = Field(default=None, foreign_key='conversationcategory.id')
    title: str
    description: str
    system_prompt: str
    initial_prompt: str
    ai_setup: dict = Field(default_factory=dict, sa_column=Column(JSON))
    language_code: str = Field(foreign_key='language.code')
    status: ScenarioTemplateStatus = Field(default=ScenarioTemplateStatus.draft)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), alias='createdAt')
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), alias='updatedAt')

    # Relationships
    category: Optional['ConversationCategory'] = Relationship(back_populates='scenario_templates')
    language: Optional['Language'] = Relationship()
    training_cases: list['TrainingCase'] = Relationship(
        back_populates='scenario_template', cascade_delete=True, alias='trainingCases'
    )

    # Needed for Column(JSON)
    class Config:  # type: ignore
        arbitrary_types_allowed = True


@event.listens_for(ScenarioTemplate, 'before_update')
def update_timestamp(mapper: Mapper, connection: Connection, target: ScenarioTemplate) -> None:
    target.updated_at = datetime.now(UTC)


# Schema for creating a new ScenarioTemplate
class ScenarioTemplateCreate(CamelModel):
    category_id: Optional[UUID] = None
    title: str
    description: str
    system_prompt: str
    initial_prompt: str
    ai_setup: dict = Field(default_factory=dict, sa_column=Column(JSON))
    language_code: str
    status: ScenarioTemplateStatus = ScenarioTemplateStatus.draft


# Schema for reading ScenarioTemplate data
class ScenarioTemplateRead(CamelModel):
    id: UUID
    category_id: Optional[UUID]
    title: str
    description: str
    system_prompt: str
    initial_prompt: str
    ai_setup: dict = Field(default_factory=dict, sa_column=Column(JSON))
    language_code: str
    status: ScenarioTemplateStatus
    created_at: datetime = Field(alias='createdAt')
    updated_at: datetime = Field(alias='updatedAt')
