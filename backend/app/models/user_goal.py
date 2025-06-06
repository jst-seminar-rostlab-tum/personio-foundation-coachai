from datetime import UTC, datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import event
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Mapper
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.goal import Goal
    from app.models.user_profile import UserProfile


class UserGoal(SQLModel, table=True):  # `table=True` makes it a database table
    # Cannot be a foreign key because (id, language_code) is a composite primary key in Goal
    goal_id: UUID = Field(primary_key=True)
    user_id: UUID = Field(foreign_key='userprofile.id', primary_key=True)  # FK to UserProfileModel
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    goal: Optional["Goal"] = Relationship(
        back_populates="user_goals",
        sa_relationship_kwargs={
            "primaryjoin": "foreign(UserGoal.goal_id) == Goal.id"
        }
    )
    user: Optional['UserProfile'] = Relationship(back_populates='user_goals')


@event.listens_for(UserGoal, 'before_update')
def update_timestamp(mapper: Mapper, connection: Connection, target: 'UserGoal') -> None:
    target.updated_at = datetime.now(UTC)


# Schema for creating a new UserGoal
class UserGoalCreate(SQLModel):
    goal_id: UUID
    user_id: UUID


# Schema for reading UserGoal data
class UserGoalRead(SQLModel):
    goal_id: UUID
    user_id: UUID
    updated_at: datetime
