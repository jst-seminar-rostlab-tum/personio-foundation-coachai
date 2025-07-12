from datetime import UTC, datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import event
from sqlalchemy.engine.base import Connection
from sqlalchemy.orm.mapper import Mapper
from sqlmodel import Field, Relationship

from app.enums.conversation_scenario_status import ConversationScenarioStatus
from app.enums.difficulty_level import DifficultyLevel
from app.enums.language import LanguageCode
from app.models.camel_case import CamelModel

if TYPE_CHECKING:
    from app.models.conversation_category import ConversationCategory
    from app.models.scenario_preparation import ScenarioPreparation
    from app.models.session import Session
    from app.models.user_profile import UserProfile


class ConversationScenario(CamelModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key='userprofile.id', nullable=False, ondelete='CASCADE')
    category_id: str | None = Field(
        default=None, foreign_key='conversationcategory.id', ondelete='CASCADE'
    )
    custom_category_label: str | None = None
    language_code: LanguageCode = Field(default=LanguageCode.en)
    persona: str
    situational_facts: str
    difficulty_level: DifficultyLevel = Field(default=DifficultyLevel.easy)
    status: ConversationScenarioStatus = Field(default=ConversationScenarioStatus.draft)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    category: Optional['ConversationCategory'] = Relationship(
        back_populates='conversation_scenarios'
    )
    sessions: list['Session'] = Relationship(back_populates='scenario', cascade_delete=True)
    preparation: Optional['ScenarioPreparation'] = Relationship(
        back_populates='scenario', cascade_delete=True
    )
    user_profile: Optional['UserProfile'] = Relationship(back_populates='conversation_scenarios')


@event.listens_for(ConversationScenario, 'before_update')
def update_timestamp(
    mapper: Mapper, connection: Connection, target: 'ConversationScenario'
) -> None:
    target.updated_at = datetime.now(UTC)
