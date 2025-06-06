from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, event
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Mapper
from sqlmodel import Field, Relationship, SQLModel

from app.models.user_confidence_score import ConfidenceScoreRead

if TYPE_CHECKING:
    from app.models.experience import Experience
    from app.models.learning_style import LearningStyle
    from app.models.rating import Rating
    from app.models.session_length import SessionLength
    from app.models.training_case import TrainingCase
    from app.models.user_confidence_score import UserConfidenceScore
    from app.models.user_goal import UserGoal


class UserRole(str, Enum):
    user = 'user'
    admin = 'admin'


class UserProfile(SQLModel, table=True):  # `table=True` makes it a database table
    id: UUID = Field(
        default_factory=uuid4, sa_column=Column(PG_UUID(as_uuid=True), primary_key=True)
    )
    user_name: Optional[str] = None
    preferred_language: str = Field(foreign_key='language.code')  # FK to LanguageModel
    experience_id: UUID = Field(foreign_key='experience.id')  # FK to Experience
    preferred_learning_style_id: UUID = Field(foreign_key='learningstyle.id')
    preferred_session_length_id: UUID = Field(foreign_key='sessionlength.id')
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    store_conversations: bool = Field(default=True)
    # Relationships
    ratings: Optional['Rating'] = Relationship(back_populates='user', cascade_delete=True)
    training_cases: list['TrainingCase'] = Relationship(back_populates='user', cascade_delete=True)
    role: Optional[UserRole] = Field(default=UserRole.user)
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

    # User Statistics
    total_sessions: int = Field(default=0)
    training_time: float = Field(default=0)  # in hours
    current_streak_days: int = Field(default=0)
    average_score: int = Field(default=0)
    goals_achieved: int = Field(default=0)
    # TODO: Add performance_over_time and skills_performance


# Automatically update `updated_at` before an update
@event.listens_for(UserProfile, 'before_update')
def update_timestamp(mapper: Mapper, connection: Connection, target: 'UserProfile') -> None:
    target.updated_at = datetime.now(UTC)


# Schema for creating a new UserProfile
class UserProfileCreate(SQLModel):
    preferred_language: str
    role: UserRole
    experience_id: UUID
    preferred_learning_style_id: UUID
    preferred_session_length_id: UUID
    store_conversations: bool
    goal_ids: list[UUID]
    confidence_scores: list[dict]


# Schema for reading UserProfile data
class UserProfileRead(SQLModel):
    id: UUID
    preferred_language: str
    role: UserRole | None
    experience_id: UUID
    preferred_learning_style_id: UUID
    preferred_session_length_id: UUID
    goal: list[UUID]
    confidence_scores: list[UUID]
    store_conversations: bool
    updated_at: datetime


class UserProfileExtendedRead(SQLModel):
    user_id: UUID
    preferred_language: str
    role: Optional[UserRole]
    experience: Optional[str]
    preferred_learning_style: Optional[str]
    preferred_session_length: Optional[str]
    goal: list[str]
    confidence_scores: list[ConfidenceScoreRead]
    store_conversations: bool


UserProfileExtendedRead.model_rebuild()


# Schema for reading User Statistics
class UserStatisticsRead(SQLModel):
    total_sessions: int
    training_time: float  # in hours
    current_streak_days: int
    average_score: int
    goals_achieved: int
    performance_over_time: list[int]
    skills_performance: dict[str, int]
