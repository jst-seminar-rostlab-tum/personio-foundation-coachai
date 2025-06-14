from app.models.camel_case import CamelModel
from app.models.user_confidence_score import ConfidenceArea
from app.models.user_goal import Goal
from app.models.user_profile import AccountRole, Experience, PreferredLearningStyle


class PersonalizationOptionRead(CamelModel):
    roles: list[AccountRole]
    experiences: list[Experience]
    goals: list[Goal]
    confidence_areas: list[ConfidenceArea]
    learning_styles: list[PreferredLearningStyle]
