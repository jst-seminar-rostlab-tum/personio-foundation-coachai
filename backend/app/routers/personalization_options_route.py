from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.database import get_session
from app.models.confidence_area import ConfidenceArea, ConfidenceAreaRead
from app.models.experience import Experience, ExperienceRead
from app.models.goal import Goal, GoalRead
from app.models.language import Language, LanguageRead
from app.models.learning_style import LearningStyle, LearningStyleRead
from app.models.personalization_option import PersonalizationOptionRead
from app.models.role import Role, RoleRead
from app.models.session_length import SessionLength, SessionLengthRead

router = APIRouter(prefix='/personalization-options', tags=['Personalization Options'])


@router.get('/', response_model=PersonalizationOptionRead)
def get_personalization_options(
    session: Annotated[Session, Depends(get_session)],
) -> PersonalizationOptionRead:
    """
    Retrieve all personalization options related to the user.
    """
    experiences = session.exec(select(Experience)).all()
    roles = session.exec(select(Role)).all()
    goals = session.exec(select(Goal)).all()
    confidence_areas = session.exec(select(ConfidenceArea)).all()
    languages = session.exec(select(Language)).all()
    learning_styles = session.exec(select(LearningStyle)).all()
    session_lengths = session.exec(select(SessionLength)).all()

    return PersonalizationOptionRead(
        roles=[RoleRead(**roles.dict()) for roles in roles],
        experiences=[
            ExperienceRead(
                id=experience.id, label=experience.label, description=experience.description
            )
            for experience in experiences
        ],
        goals=[
            GoalRead(id=goal.id, label=goal.label, description=goal.description) for goal in goals
        ],
        confidence_areas=[
            ConfidenceAreaRead(
                id=confidence_area.id,
                label=confidence_area.label,
                description=confidence_area.description,
                min_value=confidence_area.min_value,
                max_value=confidence_area.max_value,
                min_label=confidence_area.min_label,
                max_label=confidence_area.max_label,
            )
            for confidence_area in confidence_areas
        ],
        languages=[LanguageRead(code=language.code, name=language.name) for language in languages],
        learning_styles=[
            LearningStyleRead(
                id=learning_style.id,
                label=learning_style.label,
                description=learning_style.description,
            )
            for learning_style in learning_styles
        ],
        session_lengths=[
            SessionLengthRead(
                id=session_length.id,
                label=session_length.label,
                description=session_length.description,
            )
            for session_length in session_lengths
        ],
    )
