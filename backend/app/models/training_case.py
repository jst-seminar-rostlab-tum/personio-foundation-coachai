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
    user_id: UUID = Field(foreign_key='userprofile.id', nullable=False)  # FK to UserProfile
    category_id: UUID | None = Field(default=None, foreign_key='conversationcategory.id')
    custom_category_label: str | None = None
    context: str
    goal: str
    other_party: str
    difficulty_id: UUID = Field(default=None, foreign_key='difficultylevel.id')
    tone: str | None = None
    complexity: str | None = None
    status: TrainingCaseStatus = Field(default=TrainingCaseStatus.draft)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    category: Optional['ConversationCategory'] = Relationship(back_populates='training_cases')
    sessions: list['TrainingSession'] = Relationship(back_populates='case', cascade_delete=True)
    preparations: list['TrainingPreparation'] = Relationship(
        back_populates='case', cascade_delete=True
    )
    user: Optional['UserProfile'] = Relationship(back_populates='training_cases')
    difficulty_level: Optional['DifficultyLevel'] = Relationship(back_populates='training_cases')


@event.listens_for(TrainingCase, 'before_update')
def update_timestamp(mapper: Mapper, connection: Connection, target: 'TrainingCase') -> None:
    target.updated_at = datetime.now(UTC)


# Schema for creating a new TrainingCase
class TrainingCaseCreate(SQLModel):
    user_id: UUID
    category_id: UUID | None = None
    custom_category_label: str | None = None
    context: str
    goal: str
    other_party: str
    difficulty_id: UUID
    tone: str | None = None
    complexity: str | None = None
    status: TrainingCaseStatus = TrainingCaseStatus.draft


# Schema for reading TrainingCase data
class TrainingCaseRead(SQLModel):
    id: UUID
    user_id: UUID
    category_id: UUID | None
    custom_category_label: str | None
    context: str
    goal: str
    other_party: str
    difficulty_id: UUID
    tone: str | None
    complexity: str | None
    status: TrainingCaseStatus
    created_at: datetime
    updated_at: datetime
