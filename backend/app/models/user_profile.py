from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import event
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Mapper
from sqlmodel import Field, Relationship

from app.enums.account_role import AccountRole
from app.enums.experience import Experience
from app.enums.language import LanguageCode
from app.enums.preferred_learning_style import PreferredLearningStyle
from app.enums.professional_role import ProfessionalRole
from app.models.camel_case import CamelModel

if TYPE_CHECKING:
    from app.models.conversation_scenario import ConversationScenario
    from app.models.review import Review
    from app.models.user_confidence_score import UserConfidenceScore
    from app.models.user_goal import UserGoal


class UserProfile(CamelModel, table=True):  # `table=True` makes it a database table
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    full_name: str = Field(max_length=100)
    email: str = Field(max_length=100, unique=True)
    phone_number: str = Field(max_length=15, unique=True)
    preferred_language_code: LanguageCode = Field(default=LanguageCode.en)
    experience: Experience = Field(default=Experience.beginner)
    preferred_learning_style: PreferredLearningStyle = Field(default=PreferredLearningStyle.visual)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_logged_in: datetime = Field(default_factory=lambda: datetime.now(UTC))
    store_conversations: bool = Field(default=True)
    # Relationships
    reviews: list['Review'] = Relationship(back_populates='user_profile', cascade_delete=True)

    conversation_scenarios: list['ConversationScenario'] = Relationship(
        back_populates='user_profile', cascade_delete=True
    )
    account_role: AccountRole = Field(default=AccountRole.user)
    professional_role: ProfessionalRole = Field(default=ProfessionalRole.hr_professional)
    user_goals: list['UserGoal'] = Relationship(
        back_populates='user', cascade_delete=True
    )  # Add this line
    user_confidence_scores: list['UserConfidenceScore'] = Relationship(
        back_populates='user', cascade_delete=True
    )

    # User Statistics
    current_streak_days: int = Field(default=0)
    total_sessions: int = Field(default=0)
    training_time: float = Field(default=0)  # in hours
    current_streak_days: int = Field(default=0)
    score_sum: float = Field(default=0)
    goals_achieved: int = Field(default=0)
    # TODO: Add performance_over_time and skills_performance


@event.listens_for(UserProfile, 'before_update')
def update_timestamp(mapper: Mapper, connection: Connection, target: 'UserProfile') -> None:
    target.updated_at = datetime.now(UTC)
