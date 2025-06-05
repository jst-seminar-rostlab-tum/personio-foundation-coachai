from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user_goal import UserGoal


class Goal(BaseModel, table=True):  # `table=True` makes it a database table
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    label: str
    description: str

    # Relationships
    user_goals: list['UserGoal'] = Relationship(back_populates='goal', cascade_delete=True)


# Schema for creating a new Goal
class GoalCreate(BaseModel):
    label: str
    description: str


# Schema for reading Goal data
class GoalRead(BaseModel):
    id: UUID
    label: str
    description: str
