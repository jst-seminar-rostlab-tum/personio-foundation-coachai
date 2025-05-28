from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import event
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Mapper
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from backend.models.experience import Experience
    from backend.models.rating import Rating
    from backend.models.role import Role
    from backend.models.training_case import TrainingCase
    from backend.models.user_goal import UserGoal


class UserProfile(SQLModel, table=True):  # `table=True` makes it a database table
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    preferred_language: str = Field(foreign_key='language.code')  # FK to LanguageModel
    role_id: UUID = Field(foreign_key='role.id')  # FK to Role
    experience_id: UUID = Field(foreign_key='experience.id')  # FK to Experience
    preferred_learning_style: str
    preferred_session_length: str
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None

    # Relationships
    ratings: Optional['Rating'] = Relationship(back_populates='user', cascade_delete=True)
    training_cases: Optional['TrainingCase'] = Relationship(
        back_populates='user', cascade_delete=True
    )
    role: Optional['Role'] = Relationship(back_populates='user_profiles')  # Use string reference
    experience: Optional['Experience'] = Relationship(back_populates='user')
    user_goals: list['UserGoal'] = Relationship(
        back_populates='user', cascade_delete=True
    )  # Add this line


# Automatically update `updated_at` before an update
@event.listens_for(UserProfile, 'before_update')
def update_timestamp(mapper: Mapper, connection: Connection, target: 'UserProfile') -> None:
    target.updated_at = datetime.utcnow()


# Schema for creating a new UserProfile
class UserProfileCreate(SQLModel):
    preferred_language: str
    role_id: UUID
    experience_id: UUID
    preferred_learning_style: str
    preferred_session_length: str


# Schema for reading UserProfile data
class UserProfileRead(SQLModel):
    id: UUID
    preferred_language: str
    role_id: UUID
    experience_id: UUID
    preferred_learning_style: str
    preferred_session_length: str
    updated_at: datetime
    deleted_at: Optional[datetime]
