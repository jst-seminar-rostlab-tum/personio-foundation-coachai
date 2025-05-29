from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from backend.models.user_goal import UserGoal


class Goal(SQLModel, table=True):  # `table=True` makes it a database table
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    label: str
    description: str

    # Relationships
    user_goals: list['UserGoal'] = Relationship(back_populates='goal')


# Schema for creating a new Goal
class GoalCreate(SQLModel):
    label: str
    description: str


# Schema for reading Goal data
class GoalRead(SQLModel):
    id: UUID
    label: str
    description: str
