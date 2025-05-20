from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import uuid4, UUID
from typing import Optional, List
from enum import Enum

class ScenarioTemplateStatus(str, Enum):
    draft = "draft"
    ready = "ready"
    archived = "archived"

# Database model
class ScenarioTemplateModel(SQLModel, table=True):  # `table=True` makes it a database table
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    category_id: Optional[UUID] = Field(default=None, foreign_key="conversationcategorymodel.id")
    title: str
    description: str
    system_prompt: str
    initial_prompt: str
    ai_setup: str
    language_code: str = Field(foreign_key="languagemodel.code")
    status: ScenarioTemplateStatus = Field(default=ScenarioTemplateStatus.draft)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    category: Optional["ConversationCategoryModel"] = Relationship()
    language: Optional["LanguageModel"] = Relationship()
    training_cases: List["TrainingCaseModel"] = Relationship(back_populates="scenario_template")

# Schema for creating a new ScenarioTemplate
class ScenarioTemplateCreate(SQLModel):
    category_id: Optional[UUID] = None
    title: str
    description: str
    system_prompt: str
    initial_prompt: str
    ai_setup: str
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
    ai_setup: str
    language_code: str
    status: ScenarioTemplateStatus
    created_at: datetime
    updated_at: datetime