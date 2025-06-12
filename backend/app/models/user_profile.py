from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import event
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Mapper
from sqlmodel import Field, Relationship

from app.models.camel_case import CamelModel
from app.models.language import LanguageCode
from app.models.user_confidence_score import ConfidenceScoreRead

if TYPE_CHECKING:
    from app.models.conversation_scenario import ConversationScenario
    from app.models.rating import Rating
    from app.models.user_confidence_score import UserConfidenceScore
    from app.models.user_goal import UserGoal


class AccountRole(str, Enum):
    user = 'user'
    admin = 'admin'

class ProfessionalRole(str, Enum):
    hr_professional = 'hr_professional'
    team_leader = 'team_leader'
    executive = 'executive'
    other = 'other'

class Experience(str, Enum):
    beginner = 'beginner'
    intermediate = 'intermediate'
    skilled = 'skilled'
    advanced = 'advanced'
    expert = 'expert'

class PreferredLearningStyle(str, Enum):
    visual = 'visual'
    auditory = 'auditory'
    kinesthetic = 'kinesthetic'

class UserProfile(CamelModel, table=True):  # `table=True` makes it a database table
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    preferred_language_code: LanguageCode = Field(default=LanguageCode.en)
    experience: Experience = Field(default=Experience.beginner)
    preferred_learning_style: PreferredLearningStyle = Field(default=PreferredLearningStyle.visual)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    store_conversations: bool = Field(default=True)
    # Relationships
    ratings: Optional['Rating'] = Relationship(back_populates='user', cascade_delete=True)
    conversation_scenarios: list['ConversationScenario'] = Relationship(
        back_populates='user_profile', cascade_delete=True
    )
    account_role: Optional[AccountRole] = Field(default=AccountRole.user)
    professional_role: Optional[ProfessionalRole] = Field(default=ProfessionalRole.hr_professional)
    user_goals: list['UserGoal'] = Relationship(
        back_populates='user', cascade_delete=True
    )  # Add this line
    user_confidence_scores: list['UserConfidenceScore'] = Relationship(
        back_populates='user', cascade_delete=True
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
class UserProfileCreate(CamelModel):
    preferred_language_code: LanguageCode
    account_role: AccountRole
    professional_role: ProfessionalRole
    experience: Experience
    preferred_learning_style: PreferredLearningStyle
    store_conversations: bool
    goal_ids: list[UUID]
    confidence_scores: list[dict]


# Schema for reading UserProfile data
class UserProfileRead(CamelModel):
    id: UUID
    preferred_language_code: LanguageCode
    account_role: AccountRole
    professional_role: ProfessionalRole
    experience: Experience
    preferred_learning_style: PreferredLearningStyle
    goal: list[UUID]
    confidence_scores: list[UUID]
    store_conversations: bool
    updated_at: datetime


class UserProfileExtendedRead(CamelModel):
    user_id: UUID
    preferred_language_code: LanguageCode
    account_role: Optional[AccountRole]
    professional_role: Optional[ProfessionalRole]
    experience: Optional[Experience]
    preferred_learning_style: Optional[PreferredLearningStyle]
    goal: list[str]
    confidence_scores: list[ConfidenceScoreRead]
    store_conversations: bool


UserProfileExtendedRead.model_rebuild()


# Schema for reading User Statistics
class UserStatisticsRead(CamelModel):
    total_sessions: int
    training_time: float  # in hours
    current_streak_days: int
    average_score: int
    goals_achieved: int
    performance_over_time: list[int]
    skills_performance: dict[str, int]
