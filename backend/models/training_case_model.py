from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import event
from sqlmodel import Field, Relationship, SQLModel


# Enum for status
class TrainingCaseStatus(str, Enum):
    draft = "draft"
    ready = "ready"
    archived = "archived"

# Database model
class TrainingCaseModel(SQLModel, table=True):  # `table=True` makes it a database table
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="userprofilemodel.id", nullable=False)  # FK to UserProfileModel
    category_id: Optional[UUID] = Field(default=None, foreign_key="conversationcategorymodel.id")
    scenario_template_id: Optional[UUID] = Field(default=None, foreign_key="scenariotemplatemodel.id")
    custom_category_label: Optional[str] = None
    context: str
    goal: str
    other_party: str
    difficulty_id: UUID
    tone: Optional[str] = None
    complexity: Optional[str] = None
    status: TrainingCaseStatus = Field(default=TrainingCaseStatus.draft)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    category: Optional["ConversationCategoryModel"] = Relationship(back_populates="training_cases")
    sessions: List["TrainingSessionModel"] = Relationship(back_populates="case")
    scenario_template: Optional["ScenarioTemplateModel"] = Relationship()
    preparations: List["TrainingPreparationModel"] = Relationship(back_populates="case")
    user: Optional["UserProfileModel"] = Relationship(back_populates="training_cases")
@event.listens_for(TrainingCaseModel, "before_update")
def update_timestamp(mapper, connection, target) -> None:
    target.updated_at = datetime.utcnow()
# Schema for creating a new TrainingCase
class TrainingCaseCreate(SQLModel):
    user_id: UUID
    category_id: Optional[UUID] = None
    scenario_template_id: Optional[UUID] = None
    custom_category_label: Optional[str] = None
    context: str
    goal: str
    other_party: str
    difficulty_id: UUID
    tone: Optional[str] = None
    complexity: Optional[str] = None
    status: TrainingCaseStatus = TrainingCaseStatus.draft

# Schema for reading TrainingCase data
class TrainingCaseRead(SQLModel):
    id: UUID
    user_id: UUID
    category_id: Optional[UUID]
    scenario_template_id: Optional[UUID]
    custom_category_label: Optional[str]
    context: str
    goal: str
    other_party: str
    difficulty_id: UUID
    tone: Optional[str]
    complexity: Optional[str]
    status: TrainingCaseStatus
    created_at: datetime
    updated_at: datetime