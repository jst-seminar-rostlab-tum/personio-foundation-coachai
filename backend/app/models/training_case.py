from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import event
from sqlalchemy.engine.base import Connection
from sqlalchemy.orm.mapper import Mapper
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.conversation_category import ConversationCategory
    from app.models.difficulty_level import DifficultyLevel
    from app.models.training_preparation import TrainingPreparation
    from app.models.training_session import TrainingSession
    from app.models.user_profile import UserProfile


# Enum for status
class TrainingCaseStatus(str, Enum):
    draft = 'draft'
    ready = 'ready'
    archived = 'archived'


# Database model
class TrainingCase(SQLModel, table=True):  # `table=True` makes it a database table
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    language_code: str = Field(primary_key=True)  # e.g., 'en', 'fr', 'de'
    user_id: UUID = Field(foreign_key='userprofile.id', nullable=False)  # FK to UserProfile
    category_id: Optional[UUID] = Field(default=None, foreign_key='conversationcategory.id')
    custom_category_label: Optional[str] = None
    context: str
    goal: str
    other_party: str
    difficulty_id: UUID = Field(default=None, foreign_key='difficultylevel.id')
    tone: Optional[str] = None
    complexity: Optional[str] = None
    status: TrainingCaseStatus = Field(default=TrainingCaseStatus.draft)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    category: Optional['ConversationCategory'] = Relationship(back_populates='training_cases')
    sessions: list['TrainingSession'] = Relationship(
        back_populates='case',
        sa_relationship_kwargs={
            "primaryjoin": "foreign(TrainingSession.case_id) == TrainingCase.id"
        }
    )
    preparations: list['TrainingPreparation'] = Relationship(
        back_populates='case',
        sa_relationship_kwargs={
            "primaryjoin": "foreign(TrainingPreparation.case_id) == TrainingCase.id"
        }
    )
    user: Optional['UserProfile'] = Relationship(back_populates='training_cases')
    difficulty_level: Optional['DifficultyLevel'] = Relationship(back_populates='training_cases')


@event.listens_for(TrainingCase, 'before_update')
def update_timestamp(mapper: Mapper, connection: Connection, target: 'TrainingCase') -> None:
    target.updated_at = datetime.now(UTC)


# Schema for creating a new TrainingCase
class TrainingCaseCreate(SQLModel):
    id: Optional[UUID] = None
    language_code: str
    user_id: UUID
    category_id: Optional[UUID] = None
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
    language_code: str
    user_id: UUID
    category_id: Optional[UUID]
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
