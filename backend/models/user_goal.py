from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import event
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Mapper
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from backend.models.goal import Goal
    from backend.models.user_profile import UserProfile


class UserGoal(SQLModel, table=True):  # `table=True` makes it a database table
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    goal_id: UUID = Field(foreign_key='goal.id')  # FK to Goal
    user_id: UUID = Field(foreign_key='userprofile.id')  # FK to UserProfileModel
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    goal: Optional['Goal'] = Relationship(back_populates='user_goals')
    user: Optional['UserProfile'] = Relationship(back_populates='user_goals')


@event.listens_for(UserGoal, 'before_update')
def update_timestamp(mapper: Mapper, connection: Connection, target: 'UserGoal') -> None:
    target.updated_at = datetime.utcnow()


# Schema for creating a new UserGoal
class UserGoalCreate(SQLModel):
    goal_id: UUID
    user_id: UUID


# Schema for reading UserGoal data
class UserGoalRead(SQLModel):
    id: UUID
    goal_id: UUID
    user_id: UUID
    updated_at: datetime
