from sqlmodel import SQLModel

from app.models.confidence_area import ConfidenceAreaRead
from app.models.experience import ExperienceRead
from app.models.goal import GoalRead
from app.models.language import LanguageRead
from app.models.learning_style import LearningStyleRead
from app.models.role import RoleRead
from app.models.session_length import SessionLengthRead


class PersonalizationOptionRead(SQLModel):
    roles: list[RoleRead]
    experiences: list[ExperienceRead]
    goals: list[GoalRead]
    confidence_areas: list[ConfidenceAreaRead]
    languages: list[LanguageRead]
    learning_styles: list[LearningStyleRead]
    session_lengths: list[SessionLengthRead]
