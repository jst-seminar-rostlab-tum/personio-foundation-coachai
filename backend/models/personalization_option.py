from sqlmodel import SQLModel

from .confidence_area import ConfidenceAreaRead
from .experience import ExperienceRead
from .goal import GoalRead
from .language import LanguageRead
from .learning_style import LearningStyleRead
from .role import RoleRead
from .session_length import SessionLengthRead


class PersonalizationOptionRead(SQLModel):
    roles: list[RoleRead]
    experiences: list[ExperienceRead]
    goals: list[GoalRead]
    confidence_areas: list[ConfidenceAreaRead]
    languages: list[LanguageRead]
    learning_styles: list[LearningStyleRead]
    session_lengths: list[SessionLengthRead]
