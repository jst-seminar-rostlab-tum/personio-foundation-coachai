from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import event
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Mapper
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .scenario_template import ScenarioTemplate
    from .training_case import TrainingCase


class ConversationCategory(SQLModel, table=True):  # `table=True` makes it a database table
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(unique=True)
    icon_uri: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    training_cases: list['TrainingCase'] = Relationship(
        back_populates='category', cascade_delete=True
    )
    scenario_templates: list['ScenarioTemplate'] = Relationship(
        back_populates='category', cascade_delete=True
    )


@event.listens_for(ConversationCategory, 'before_update')
def update_timestamp(
    mapper: Mapper, connection: Connection, target: 'ConversationCategory'
) -> None:
    target.updated_at = datetime.utcnow()


# Schema for creating a new ConversationCategory
class ConversationCategoryCreate(SQLModel):
    name: str
    icon_uri: str


# Schema for reading ConversationCategory data
class ConversationCategoryRead(SQLModel):
    id: UUID
    name: str
    icon_uri: str
    created_at: datetime
    updated_at: datetime
