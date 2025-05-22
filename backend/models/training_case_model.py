from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import event
from sqlalchemy.engine.base import Connection
from sqlalchemy.orm.mapper import Mapper
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .conversation_category_model import ConversationCategory
    from .scenario_template_model import ScenarioTemplateModel
    from .training_preparation_model import TrainingPreparationModel
    from .training_session_model import TrainingSessionModel
    from .user_profile_model import UserProfileModel


# Enum for status
class TrainingCaseStatus(str, Enum):
    draft = 'draft'
    ready = 'ready'
    archived = 'archived'


# Database model
class TrainingCaseModel(SQLModel, table=True):  # `table=True` makes it a database table
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(
        foreign_key='userprofilemodel.id', nullable=False
    )  # FK to UserProfileModel
    category_id: Optional[UUID] = Field(default=None, foreign_key='conversationcategorymodel.id')
    scenario_template_id: Optional[UUID] = Field(
        default=None, foreign_key='scenariotemplatemodel.id'
    )
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

    category: Optional['ConversationCategory'] = Relationship(back_populates='training_cases')
    sessions: list['TrainingSessionModel'] = Relationship(back_populates='case')
    scenario_template: Optional['ScenarioTemplateModel'] = Relationship()
    preparations: list['TrainingPreparationModel'] = Relationship(back_populates='case')
    user: Optional['UserProfileModel'] = Relationship(back_populates='training_cases')


@event.listens_for(TrainingCaseModel, 'before_update')
def update_timestamp(mapper: Mapper, connection: Connection, target: 'TrainingCaseModel') -> None:
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
