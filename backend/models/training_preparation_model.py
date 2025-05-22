from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import event
from sqlalchemy.engine.base import Connection
from sqlalchemy.orm.mapper import Mapper
from sqlmodel import JSON, Column, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from backend.models.training_case_model import TrainingCaseModel


class TrainingPreparationStatus(str, Enum):
    pending = 'pending'
    completed = 'completed'
    failed = 'failed'


# Database model
class TrainingPreparationModel(SQLModel, table=True):  # `table=True` makes it a database table
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    case_id: UUID = Field(foreign_key='trainingcasemodel.id')
    key_concepts: dict = Field(default_factory=dict, sa_column=Column(JSON))
    prep_checklist: dict = Field(default_factory=dict, sa_column=Column(JSON))
    status: TrainingPreparationStatus = Field(default=TrainingPreparationStatus.pending)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    case: Optional['TrainingCaseModel'] = Relationship(back_populates='preparations')

    # Automatically update `updated_at` before an update


@event.listens_for(TrainingPreparationModel, 'before_update')
def update_timestamp(
    mapper: Mapper, connection: Connection, target: 'TrainingPreparationModel'
) -> None:
    target.updated_at = datetime.utcnow()


# Schema for creating a new TrainingPreparation
class TrainingPreparationCreate(SQLModel):
    case_id: UUID
    key_concepts: dict = Field(default_factory=dict, sa_column=Column(JSON))
    prep_checklist: dict = Field(default_factory=dict, sa_column=Column(JSON))
    status: TrainingPreparationStatus = TrainingPreparationStatus.pending


# Schema for reading TrainingPreparation data
class TrainingPreparationRead(SQLModel):
    id: UUID
    case_id: UUID
    key_concepts: dict = Field(default_factory=dict, sa_column=Column(JSON))
    prep_checklist: dict = Field(default_factory=dict, sa_column=Column(JSON))
    status: TrainingPreparationStatus
    created_at: datetime
    updated_at: datetime
