from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlmodel import Session

from app.database import get_session
from app.models.user_profile import UserProfile, UserStatisticsRead

router = APIRouter(prefix='/user', tags=['User Stats'])


@router.get('/', response_model=UserStatisticsRead)
def get_user_stats(
    session: Annotated[Session, Depends(get_session)],
    x_user_id: str = Header(...),  # Auth via header
    # TODO: Adjust to the authentication token in the header
) -> UserStatisticsRead:
    try:
        user_id = UUID(x_user_id)
    except ValueError as err:
        raise HTTPException(
            status_code=401, detail='Invalid or missing authentication token'
        ) from err

    user = session.get(UserProfile, user_id)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    return UserStatisticsRead(
        total_sessions=user.total_sessions,
        training_time=user.training_time,
        current_streak_days=user.current_streak_days,
        average_score=user.average_score,
        goals_achieved=user.goals_achieved,
        # TODO: Uncomment and implement these fields when ready
        # performance_over_time=user.performance_over_time,
        # skills_performance=user.skills_performance
        # Mockked data for now
        performance_over_time=[72, 65, 70, 68, 74, 71, 78, 80, 69, 82],
        skills_performance={'structure': 85, 'empathy': 70, 'solutionFocus': 75, 'clarity': 75},
    )
