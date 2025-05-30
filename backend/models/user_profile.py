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
    full_name: str
    email: str
    phone_number: str
    password: str
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None

    # Relationships
    ratings: Optional['Rating'] = Relationship(back_populates='user')
    training_cases: Optional['TrainingCase'] = Relationship(back_populates='user')
    role: Optional['Role'] = Relationship(back_populates='user_profiles')  # Use string reference
    experience: Optional['Experience'] = Relationship(back_populates='user')
    user_goals: list['UserGoal'] = Relationship(back_populates='user')  # Add this line


# Automatically update `updated_at` before an update
@event.listens_for(UserProfile, 'before_update')
def update_timestamp(mapper: Mapper, connection: Connection, target: 'UserProfile') -> None:
    target.updated_at = datetime.utcnow()


# Schema for creating a new UserProfile
class UserProfileCreate(SQLModel):
    preferred_language: str
    role_id: Optional[UUID] = None
    experience_id: Optional[UUID] = None
    preferred_learning_style: str
    preferred_session_length: str
    email: str
    phone_number: str
    password: str
    full_name: str


# Schema for creating a new UserProfile
class UserProfileValidate(SQLModel):
    preferred_language: str
    role_id: Optional[UUID] = None
    experience_id: Optional[UUID] = None
    preferred_learning_style: str
    preferred_session_length: str
    email: str
    phone_number: str
    password: str
    full_name: str


# Schema for reading UserProfile data
class UserProfileRead(SQLModel):
    id: UUID
    preferred_language: str
    role_id: Optional[UUID] = None
    experience_id: Optional[UUID] = None
    preferred_learning_style: str
    preferred_session_length: str
    updated_at: datetime
    deleted_at: Optional[datetime]
    email: str
    phone_number: str


# Schema for sign-in credentials
class UserProfileSignIn(SQLModel):
    email: str
    password: str


# Schema for sign-in response
class UserProfileSignInResponse(SQLModel):
    id: UUID
    email: str
    full_name: str
    preferred_language: str
    role_id: Optional[UUID] = None
    experience_id: Optional[UUID] = None
    preferred_learning_style: Optional[str] = None
    preferred_session_length: Optional[str] = None


# Schema for validation response
class UserProfileValidationResponse(SQLModel):
    message: str
    is_valid: bool
    errors: Optional[dict[str, str]] = None
