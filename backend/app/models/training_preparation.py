from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import JSON, Column, event
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Mapper
from sqlmodel import Field, Relationship, SQLModel

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.training_case import TrainingCase


class TrainingPreparationStatus(str, Enum):
    pending = 'pending'
    in_progress = 'in_progress'
    completed = 'completed'
    cancelled = 'cancelled'


class KeyConcept(BaseModel):
    header: str
    value: str


# Database model
class TrainingPreparation(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    case_id: UUID = Field(foreign_key='trainingcase.id', alias='caseId')
    objectives: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    key_concepts: list[dict] = Field(default_factory=list, sa_column=Column(JSON))
    prep_checklist: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    status: TrainingPreparationStatus = Field(default=TrainingPreparationStatus.pending)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), alias='createdAt')
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), alias='updatedAt')
    case: Optional['TrainingCase'] = Relationship(back_populates='preparations')


# Automatically update `updated_at` before an update
@event.listens_for(TrainingPreparation, 'before_update')
def update_timestamp(mapper: Mapper, connection: Connection, target: 'TrainingPreparation') -> None:
    target.updated_at = datetime.now(UTC)


# Schema for creating a new TrainingPreparation
class TrainingPreparationCreate(BaseModel):
    case_id: UUID
    objectives: list[str]
    key_concepts: list[dict]
    prep_checklist: list[str]
    status: TrainingPreparationStatus


# Schema for reading TrainingPreparation data
class TrainingPreparationRead(BaseModel):
    id: UUID
    case_id: UUID
    objectives: list[str]
    key_concepts: list[dict]
    prep_checklist: list[str]
    status: TrainingPreparationStatus
    created_at: datetime
    updated_at: datetime
