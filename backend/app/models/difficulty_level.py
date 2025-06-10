from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship

from app.models.camel_case import CamelModel

if TYPE_CHECKING:
    from app.models.conversation_scenario import ConversationScenario


class DifficultyLevel(CamelModel, table=True):  # `table=True` makes it a database table
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    label: str

    # Relationships
    conversation_scenarios: list['ConversationScenario'] = Relationship(
        back_populates='difficulty_level'
    )  # Use string reference


# Schema for creating a new Role
class DifficultyLevelCreate(CamelModel):
    label: str
    description: str


# Schema for reading Role data
class DifficultyLevelRead(CamelModel):
    id: UUID
    label: str
    description: str
