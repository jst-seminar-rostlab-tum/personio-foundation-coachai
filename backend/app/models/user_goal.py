from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import event
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Mapper
from sqlmodel import Field, Relationship

from app.models.camel_case import CamelModel

if TYPE_CHECKING:
    from app.models.user_profile import UserProfile


class Goal(str, Enum):
    giving_constructive_feedback = 'giving_constructive_feedback'
    managing_team_conflicts = 'managing_team_conflicts'
    performance_reviews = 'performance_reviews'
    motivating_team_members = 'motivating_team_members'
    leading_difficult_conversations = 'leading_difficult_conversations'
    communicating_organizational_change = 'communicating_organizational_change'
    develop_emotional_intelligence = 'develop_emotional_intelligence'
    building_inclusive_teams = 'building_inclusive_teams'
    negotiation_skills = 'negotiation_skills'
    coaching_mentoring = 'coaching_mentoring'


class UserGoal(CamelModel, table=True):  # `table=True` makes it a database table
    goal: Goal = Field(default=Goal.giving_constructive_feedback, primary_key=True)
    user_id: UUID = Field(foreign_key='userprofile.id', primary_key=True)  # FK to UserProfileModel
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    user: Optional['UserProfile'] = Relationship(back_populates='user_goals')


# Automatically update `updated_at` before an update
@event.listens_for(UserGoal, 'before_update')
def update_timestamp(mapper: Mapper, connection: Connection, target: 'UserGoal') -> None:
    target.updated_at = datetime.now(UTC)


# Schema for creating a new UserGoal
class UserGoalCreate(CamelModel):
    goal: Goal
    user_id: UUID


# Schema for reading UserGoal data
class UserGoalRead(CamelModel):
    goal: Goal
    user_id: UUID
    updated_at: datetime
