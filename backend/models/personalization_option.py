from sqlmodel import SQLModel

from .confidence_area import ConfidenceAreaRead
from .experience import ExperienceRead
from .goal import GoalRead
from .language import LanguageRead
from .learning_style import LearningStyleRead
from .session_length import SessionLengthRead
from .user_profile import UserRole


class PersonalizationOptionRead(SQLModel):
    roles: list[UserRole]
    experiences: list[ExperienceRead]
    goals: list[GoalRead]
    confidence_areas: list[ConfidenceAreaRead]
    languages: list[LanguageRead]
    learning_styles: list[LearningStyleRead]
    session_lengths: list[SessionLengthRead]
