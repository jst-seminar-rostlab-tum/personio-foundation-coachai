from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import event
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Mapper
from sqlmodel import Field, Relationship, SQLModel

from backend.models.user_confidence_score import ConfidenceScoreRead

if TYPE_CHECKING:
    from backend.models.experience import Experience
    from backend.models.learning_style import LearningStyle
    from backend.models.rating import Rating
    from backend.models.role import Role
    from backend.models.session_length import SessionLength
    from backend.models.training_case import TrainingCase
    from backend.models.user_confidence_score import UserConfidenceScore
    from backend.models.user_goal import UserGoal


class UserProfile(SQLModel, table=True):  # `table=True` makes it a database table
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    preferred_language: str = Field(foreign_key='language.code')  # FK to LanguageModel
    role_id: Optional[UUID] = Field(
        default=None, foreign_key='role.id', nullable=True
    )  # FK to Role
    experience_id: Optional[UUID] = Field(
        default=None, foreign_key='experience.id', nullable=True
    )  # FK to Experience
    preferred_learning_style_id: Optional[UUID] = Field(
        default=None, foreign_key='learningstyle.id', nullable=True
    )
    preferred_session_length_id: Optional[UUID] = Field(
        default=None, foreign_key='sessionlength.id', nullable=True
    )
    full_name: str
    email: str
    phone_number: str
    password: str
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    store_conversations: bool = Field(default=True)
    # Relationships
    ratings: Optional['Rating'] = Relationship(back_populates='user', cascade_delete=True)
    training_cases: list['TrainingCase'] = Relationship(back_populates='user', cascade_delete=True)
    role: Optional['Role'] = Relationship(back_populates='user_profiles')  # Use string reference
    experience: Optional['Experience'] = Relationship(back_populates='user')
    user_goals: list['UserGoal'] = Relationship(
        back_populates='user', cascade_delete=True
    )  # Add this line
    user_confidence_scores: list['UserConfidenceScore'] = Relationship(
        back_populates='user', cascade_delete=True
    )
    preferred_learning_style: Optional['LearningStyle'] = Relationship(
        back_populates='user_profiles'
    )
    preferred_session_length: Optional['SessionLength'] = Relationship(
        back_populates='user_profiles'
    )


# Automatically update `updated_at` before an update
@event.listens_for(UserProfile, 'before_update')
def update_timestamp(mapper: Mapper, connection: Connection, target: 'UserProfile') -> None:
    target.updated_at = datetime.utcnow()


# Schema for creating a new UserProfile
class UserProfileCreate(SQLModel):
    """Schema for creating a new user profile."""

    email: str
    full_name: str
    phone_number: str
    password: str
    preferred_language: Optional[str] = None
    role_id: Optional[UUID] = None
    experience_id: Optional[UUID] = None
    preferred_learning_style_id: Optional[UUID] = None
    preferred_session_length_id: Optional[UUID] = None
    store_conversations: Optional[bool] = True


# Schema for creating a new UserProfile
class UserProfileValidate(SQLModel):
    preferred_language: str
    role_id: Optional[UUID] = None
    experience_id: Optional[UUID] = None
    preferred_learning_style_id: Optional[UUID] = None
    preferred_session_length_id: Optional[UUID] = None
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
    preferred_learning_style: Optional[UUID] = None
    preferred_session_length: Optional[UUID] = None
    updated_at: datetime
    deleted_at: Optional[datetime]
    email: str
    phone_number: str
    goal: list[UUID]
    confidence_scores: list[UUID]
    store_conversations: bool


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


class UserProfileExtendedRead(SQLModel):
    user_id: UUID
    preferred_language: str
    role: Optional[str]
    experience: Optional[str]
    preferred_learning_style: Optional[str]
    preferred_session_length: Optional[str]
    goal: list[str]
    confidence_scores: list[ConfidenceScoreRead]
    store_conversations: bool


UserProfileExtendedRead.model_rebuild()
