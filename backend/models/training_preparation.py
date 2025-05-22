from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import event
from sqlmodel import JSON, Column, Field, Relationship, SQLModel


class TrainingPreparationStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"

# Database model
class TrainingPreparation(SQLModel, table=True):  # `table=True` makes it a database table
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    case_id: UUID = Field(foreign_key="trainingcase.id")
    objectives: dict = Field(default_factory=dict, sa_column=Column(JSON))
    key_concepts: dict = Field(default_factory=dict, sa_column=Column(JSON))
    prep_checklist: dict = Field(default_factory=dict, sa_column=Column(JSON))
    status: TrainingPreparationStatus = Field(default=TrainingPreparationStatus.pending)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    case: Optional["TrainingCase"] = Relationship(back_populates="preparations")
    

    # Automatically update `updated_at` before an update
@event.listens_for(TrainingPreparation, "before_update")
def update_timestamp(mapper, connection, target) -> None:
    target.updated_at = datetime.utcnow()
# Schema for creating a new TrainingPreparation
class TrainingPreparationCreate(SQLModel):
    case_id: UUID
    objectives: dict = Field(default_factory=dict, sa_column=Column(JSON))
    key_concepts: dict = Field(default_factory=dict, sa_column=Column(JSON))
    prep_checklist: dict = Field(default_factory=dict, sa_column=Column(JSON))
    status: TrainingPreparationStatus = TrainingPreparationStatus.pending

# Schema for reading TrainingPreparation data
class TrainingPreparationRead(SQLModel):
    id: UUID
    case_id: UUID
    objectives: dict = Field(default_factory=dict, sa_column=Column(JSON))
    key_concepts: dict = Field(default_factory=dict, sa_column=Column(JSON))
    prep_checklist: dict = Field(default_factory=dict, sa_column=Column(JSON))
    status: TrainingPreparationStatus
    created_at: datetime
    updated_at: datetime