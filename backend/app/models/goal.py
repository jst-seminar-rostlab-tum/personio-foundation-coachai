from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship

from app.models.camel_case import CamelModel

if TYPE_CHECKING:
    from app.models.user_goal import UserGoal



class Goal(CamelModel, table=True):  # `table=True` makes it a database table
    # Both primary key and language code are part of the primary key
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    language_code: str = Field(primary_key=True)
    label: str
    description: str

    # Relationships
    user_goals: list["UserGoal"] = Relationship(
        back_populates="goal",
        sa_relationship_kwargs={
            "primaryjoin": "foreign(UserGoal.goal_id) == Goal.id"
        }
    )

# Schema for creating a new Goal
class GoalCreate(CamelModel):
    # `id` is optional for creation, it will be generated automatically,
    # if we want to add a new language to existing id then need to specify it
    id: Optional[UUID] = None
    language_code: str
    label: str
    description: str


# Schema for reading Goal data
class GoalRead(CamelModel):
    id: UUID
    language_code: str
    label: str
    description: str
