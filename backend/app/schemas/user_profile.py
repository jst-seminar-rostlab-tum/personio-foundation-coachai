"""Pydantic schema definitions for user profile."""

from datetime import date, datetime
from enum import Enum
from uuid import UUID

from app.enums.account_role import AccountRole
from app.enums.experience import Experience
from app.enums.language import LanguageCode
from app.enums.preferred_learning_style import PreferredLearningStyle
from app.enums.professional_role import ProfessionalRole
from app.models.camel_case import CamelModel
from app.models.user_goal import Goal
from app.schemas.conversation_scenario import ConversationScenarioCreate
from app.schemas.user_confidence_score import ConfidenceScoreRead


class ScenarioAdvice(CamelModel):
    """Schema for scenario advice."""

    mascot_speech: str
    scenario: ConversationScenarioCreate


# Schema for updating UserProfile data
class UserProfileUpdate(CamelModel):
    """Schema for user profile update."""

    preferred_language_code: LanguageCode | None = None
    account_role: AccountRole | None = None
    professional_role: ProfessionalRole | None = None
    experience: Experience | None = None
    preferred_learning_style: PreferredLearningStyle | None = None
    store_conversations: bool | None = None
    goals: list[Goal] | None = None
    confidence_scores: list[ConfidenceScoreRead] | None = None
    organization_name: str | None = None


# Schema for replacing UserProfile data
class UserProfileReplace(CamelModel):
    """Schema for user profile replace."""

    full_name: str
    preferred_language_code: LanguageCode
    account_role: AccountRole | None = None
    professional_role: ProfessionalRole
    experience: Experience
    preferred_learning_style: PreferredLearningStyle
    store_conversations: bool
    goals: list[Goal]
    confidence_scores: list[ConfidenceScoreRead]
    organization_name: str | None = None


# Schema for reading UserProfile data
class UserProfileRead(CamelModel):
    """Schema for user profile read."""

    user_id: UUID
    full_name: str
    email: str
    phone_number: str
    preferred_language_code: LanguageCode
    account_role: AccountRole
    professional_role: ProfessionalRole
    experience: Experience
    preferred_learning_style: PreferredLearningStyle
    updated_at: datetime
    store_conversations: bool
    sessions_created_today: int
    last_session_date: date
    num_remaining_daily_sessions: int
    scenario_advice: ScenarioAdvice | dict
    daily_session_limit: int
    organization_name: str | None


class UserProfileExtendedRead(UserProfileRead):
    """Schema for user profile extended read."""

    goals: list[Goal]
    confidence_scores: list[ConfidenceScoreRead]


UserProfileExtendedRead.model_rebuild()


class SessionLimitType(str, Enum):
    """Schema for session limit type."""

    DEFAULT = 'DEFAULT'
    INDIVIDUAL = 'INDIVIDUAL'


class UserProfilePaginatedRead(CamelModel):
    """Schema for user profile paginated read."""

    user_id: UUID
    email: str
    daily_session_limit: int
    limit_type: SessionLimitType


class UserListPaginatedRead(CamelModel):
    """Schema for user list paginated read."""

    page: int
    limit: int
    total_pages: int
    total_users: int
    users: list[UserProfilePaginatedRead]


# Schema for reading User Statistics
class UserStatistics(CamelModel):
    """Schema for user statistics."""

    total_sessions: int
    training_time: float  # in hours
    current_streak_days: int
    score_sum: float
    goals_achieved: int  # summation of all goals achieved
    daily_session_limit: int
    num_remaining_daily_sessions: int


class UserDailySessionLimitUpdate(CamelModel):
    """Schema for user daily session limit update."""

    daily_session_limit: int | None


class SortOption(str, Enum):
    """Schema for sort option."""

    ASC = 'ASC'
    DESC = 'DESC'
