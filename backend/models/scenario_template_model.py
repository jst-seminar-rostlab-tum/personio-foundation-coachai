from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import event
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Mapper
from sqlmodel import JSON, Column, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from backend.models.conversation_category_model import ConversationCategory
    from backend.models.language_model import LanguageModel
    from backend.models.training_case_model import TrainingCaseModel


class ScenarioTemplateStatus(str, Enum):
    draft = 'draft'
    ready = 'ready'
    archived = 'archived'


# Database model
class ScenarioTemplateModel(SQLModel, table=True):  # `table=True` makes it a database table
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    category_id: Optional[UUID] = Field(default=None, foreign_key='conversationcategory.id')
    title: str
    description: str
    system_prompt: str
    initial_prompt: str
    ai_setup: dict = Field(default_factory=dict, sa_column=Column(JSON))
    language_code: str = Field(foreign_key='languagemodel.code')
    status: ScenarioTemplateStatus = Field(default=ScenarioTemplateStatus.draft)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    category: Optional['ConversationCategory'] = Relationship()
    language: Optional['LanguageModel'] = Relationship()
    training_cases: list['TrainingCaseModel'] = Relationship(back_populates='scenario_template')

    # Needed for Column(JSON)
    class Config:
        arbitrary_types_allowed = True


@event.listens_for(ScenarioTemplateModel, 'before_update')
def update_timestamp(
    mapper: Mapper, connection: Connection, target: 'ScenarioTemplateModel'
) -> None:
    target.updated_at = datetime.utcnow()


# Schema for creating a new ScenarioTemplate
class ScenarioTemplateCreate(SQLModel):
    category_id: Optional[UUID] = None
    title: str
    description: str
    system_prompt: str
    initial_prompt: str
    ai_setup: dict = Field(default_factory=dict, sa_column=Column(JSON))
    language_code: str
    status: ScenarioTemplateStatus = ScenarioTemplateStatus.draft


# Schema for reading ScenarioTemplate data
class ScenarioTemplateRead(SQLModel):
    id: UUID
    category_id: Optional[UUID]
    title: str
    description: str
    system_prompt: str
    initial_prompt: str
    ai_setup: dict = Field(default_factory=dict, sa_column=Column(JSON))
    language_code: str
    status: ScenarioTemplateStatus
    created_at: datetime
    updated_at: datetime
