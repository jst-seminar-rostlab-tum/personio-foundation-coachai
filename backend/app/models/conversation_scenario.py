from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import event
from sqlalchemy.engine.base import Connection
from sqlalchemy.orm.mapper import Mapper
from sqlmodel import Field, Relationship

from app.models.camel_case import CamelModel

if TYPE_CHECKING:
    from app.models.conversation_category import ConversationCategory
    from app.models.difficulty_level import DifficultyLevel
    from app.models.scenario_preparation import ScenarioPreparation
    from app.models.session import Session
    from app.models.user_profile import UserProfile


# Enum for status
class ConversationScenarioStatus(str, Enum):
    draft = 'draft'
    ready = 'ready'
    archived = 'archived'


# Database model
class ConversationScenario(CamelModel, table=True):  # `table=True` makes it a database table
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key='userprofile.id', nullable=False)  # FK to UserProfile
    category_id: Optional[UUID] = Field(default=None, foreign_key='conversationcategory.id')
    custom_category_label: Optional[str] = None
    context: str
    goal: str
    other_party: str
    difficulty_id: UUID = Field(default=None, foreign_key='difficultylevel.id')
    tone: Optional[str] = None
    complexity: Optional[str] = None
    status: ConversationScenarioStatus = Field(default=ConversationScenarioStatus.draft)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    category: Optional['ConversationCategory'] = Relationship(
        back_populates='conversation_scenarios'
    )
    sessions: list['Session'] = Relationship(back_populates='scenario', cascade_delete=True)
    preparations: list['ScenarioPreparation'] = Relationship(
        back_populates='scenario', cascade_delete=True
    )
    user_profile: Optional['UserProfile'] = Relationship(back_populates='conversation_scenarios')
    difficulty_level: Optional['DifficultyLevel'] = Relationship(
        back_populates='conversation_scenarios'
    )


@event.listens_for(ConversationScenario, 'before_update')
def update_timestamp(
    mapper: Mapper, connection: Connection, target: 'ConversationScenario'
) -> None:
    target.updated_at = datetime.now(UTC)


# Schema for creating a new ConversationScenario
class ConversationScenarioCreate(CamelModel):
    user_id: UUID
    category_id: Optional[UUID] = None
    custom_category_label: Optional[str] = None
    context: str
    goal: str
    other_party: str
    difficulty_id: UUID
    tone: Optional[str] = None
    complexity: Optional[str] = None
    status: ConversationScenarioStatus = ConversationScenarioStatus.draft


# Schema for reading ConversationScenario data
class ConversationScenarioRead(CamelModel):
    id: UUID
    user_id: UUID
    category_id: Optional[UUID]
    custom_category_label: Optional[str]
    context: str
    goal: str
    other_party: str
    difficulty_id: UUID
    tone: Optional[str]
    complexity: Optional[str]
    status: ConversationScenarioStatus
    created_at: datetime
    updated_at: datetime
