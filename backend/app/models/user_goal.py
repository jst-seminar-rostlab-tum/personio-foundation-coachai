from datetime import UTC, datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import event
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Mapper
from sqlmodel import Field, Relationship

from app.enums.goal import Goal
from app.models.camel_case import CamelModel

if TYPE_CHECKING:
    from app.models.user_profile import UserProfile


class UserGoal(CamelModel, table=True):
    goal: Goal = Field(default=Goal.giving_constructive_feedback, primary_key=True)
    user_id: UUID = Field(foreign_key='userprofile.id', primary_key=True, ondelete='CASCADE')
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    user: Optional['UserProfile'] = Relationship(back_populates='user_goals')


# Automatically update `updated_at` before an update
@event.listens_for(UserGoal, 'before_update')
def update_timestamp(mapper: Mapper, connection: Connection, target: 'UserGoal') -> None:
    target.updated_at = datetime.now(UTC)
