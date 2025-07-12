from datetime import date, datetime
from uuid import UUID

from app.models.camel_case import CamelModel
from app.models.language import LanguageCode
from app.models.user_goal import Goal
from app.models.user_profile import (
    AccountRole,
    Experience,
    PreferredLearningStyle,
    ProfessionalRole,
)
from app.schemas.user_confidence_score import ConfidenceScoreRead


# Schema for updating UserProfile data
class UserProfileUpdate(CamelModel):
    preferred_language_code: LanguageCode | None = None
    account_role: AccountRole | None = None
    professional_role: ProfessionalRole | None = None
    experience: Experience | None = None
    preferred_learning_style: PreferredLearningStyle | None = None
    store_conversations: bool | None = None
    goals: list[Goal] | None = None
    confidence_scores: list[ConfidenceScoreRead] | None = None


# Schema for replacing UserProfile data
class UserProfileReplace(CamelModel):
    full_name: str
    preferred_language_code: LanguageCode
    account_role: AccountRole | None = None
    professional_role: ProfessionalRole
    experience: Experience
    preferred_learning_style: PreferredLearningStyle
    store_conversations: bool
    goals: list[Goal]
    confidence_scores: list[ConfidenceScoreRead]


# Schema for reading UserProfile data
class UserProfileRead(CamelModel):
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
    num_remaining_daily_sessions: int | None = None


class UserProfileExtendedRead(UserProfileRead):
    goals: list[Goal]
    confidence_scores: list[ConfidenceScoreRead]


UserProfileExtendedRead.model_rebuild()


class UserEmailRead(CamelModel):
    user_id: UUID
    email: str


class PaginatedUserResponse(CamelModel):
    page: int
    limit: int
    total_pages: int
    total_users: int
    users: list[UserProfileRead] | list[UserProfileExtendedRead] | list[UserEmailRead]


# Schema for reading User Statistics
class UserStatisticsRead(CamelModel):
    total_sessions: int
    training_time: float  # in hours
    current_streak_days: int
    score_sum: float
    goals_achieved: int  # summation of all goals achieved
    performance_over_time: list[int]
    skills_performance: dict[str, int]
    daily_session_limit: int | None = None
    num_remaining_daily_sessions: int
