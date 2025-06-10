from app.models.camel_case import CamelModel
from app.models.confidence_area import ConfidenceAreaRead
from app.models.experience import ExperienceRead
from app.models.goal import GoalRead
from app.models.language import LanguageRead
from app.models.learning_style import LearningStyleRead
from app.models.role import RoleRead


class PersonalizationOptionRead(CamelModel):
    roles: list[RoleRead]
    experiences: list[ExperienceRead]
    goals: list[GoalRead]
    confidence_areas: list[ConfidenceAreaRead]
    languages: list[LanguageRead]
    learning_styles: list[LearningStyleRead]
