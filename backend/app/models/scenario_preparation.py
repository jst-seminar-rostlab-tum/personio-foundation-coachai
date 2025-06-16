from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlalchemy import event
from sqlalchemy.engine.base import Connection
from sqlalchemy.orm.mapper import Mapper
from sqlmodel import JSON, Column, Field, Relationship

from app.models.camel_case import CamelModel

if TYPE_CHECKING:
    from app.models.conversation_scenario import ConversationScenario


class ScenarioPreparationStatus(str, Enum):
    pending = 'pending'
    completed = 'completed'
    failed = 'failed'


class KeyConcept(BaseModel):
    header: str
    value: str


class ScenarioPreparation(CamelModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    scenario_id: UUID = Field(foreign_key='conversationscenario.id', ondelete='CASCADE')
    objectives: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    key_concepts: list[dict] = Field(default_factory=list, sa_column=Column(JSON))
    prep_checklist: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    status: ScenarioPreparationStatus = Field(default=ScenarioPreparationStatus.pending)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    scenario: Optional['ConversationScenario'] = Relationship(back_populates='preparations')

    # Automatically update `updated_at` before an update


@event.listens_for(ScenarioPreparation, 'before_update')
def update_timestamp(mapper: Mapper, connection: Connection, target: 'ScenarioPreparation') -> None:
    target.updated_at = datetime.now(UTC)


# Schema for creating a new ScenarioPreparation
class ScenarioPreparationCreate(CamelModel):
    scenario_id: UUID
    objectives: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    key_concepts: list[KeyConcept] = Field(default_factory=list, sa_column=Column(JSON))
    prep_checklist: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    status: ScenarioPreparationStatus = Field(default=ScenarioPreparationStatus.pending)


# Schema for reading ScenarioPreparation data
class ScenarioPreparationRead(CamelModel):
    id: UUID
    scenario_id: UUID
    objectives: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    key_concepts: list[KeyConcept] = Field(default_factory=list, sa_column=Column(JSON))
    prep_checklist: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    status: ScenarioPreparationStatus
    category_name: Optional[str] = None
    context: Optional[str] = None
    goal: Optional[str] = None
    other_party: Optional[str] = None
    created_at: datetime
    updated_at: datetime
