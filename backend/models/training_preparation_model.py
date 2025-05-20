from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import uuid4, UUID
from enum import Enum
from typing import Optional

class TrainingPreparationStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"

# Database model
class TrainingPreparationModel(SQLModel, table=True):  # `table=True` makes it a database table
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    case_id: UUID = Field(foreign_key="trainingcasemodel.id")
    key_concepts: str
    prep_checklist: str
    status: TrainingPreparationStatus = Field(default=TrainingPreparationStatus.pending)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    case: Optional["TrainingCaseModel"] = Relationship(back_populates="preparations")

# Schema for creating a new TrainingPreparation
class TrainingPreparationCreate(SQLModel):
    case_id: UUID
    key_concepts: str
    prep_checklist: str
    status: TrainingPreparationStatus = TrainingPreparationStatus.pending

# Schema for reading TrainingPreparation data
class TrainingPreparationRead(SQLModel):
    id: UUID
    case_id: UUID
    key_concepts: str
    prep_checklist: str
    status: TrainingPreparationStatus
    created_at: datetime
    updated_at: datetime