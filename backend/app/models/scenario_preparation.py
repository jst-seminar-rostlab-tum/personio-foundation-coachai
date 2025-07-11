from datetime import UTC, datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import event
from sqlalchemy.engine.base import Connection
from sqlalchemy.orm.mapper import Mapper
from sqlmodel import JSON, Column, Field, Relationship

from app.enums.scenario_preparation_status import ScenarioPreparationStatus
from app.models.camel_case import CamelModel

if TYPE_CHECKING:
    from app.models.conversation_scenario import ConversationScenario


class ScenarioPreparation(CamelModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    scenario_id: UUID = Field(foreign_key='conversationscenario.id', ondelete='CASCADE')
    objectives: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    document_names: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    key_concepts: list[dict] = Field(default_factory=list, sa_column=Column(JSON))
    prep_checklist: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    status: ScenarioPreparationStatus = Field(default=ScenarioPreparationStatus.pending)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    scenario: Optional['ConversationScenario'] = Relationship(back_populates='preparation')

    # Automatically update `updated_at` before an update


@event.listens_for(ScenarioPreparation, 'before_update')
def update_timestamp(mapper: Mapper, connection: Connection, target: 'ScenarioPreparation') -> None:
    target.updated_at = datetime.now(UTC)
