from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session as DBSession
from sqlmodel import select

from app.database import get_db_session
from app.models.user_goal import UserGoal, UserGoalCreate, UserGoalRead
from app.models.user_profile import UserProfile

router = APIRouter(prefix='/user-goals', tags=['User Goals'])


@router.post('', response_model=UserGoalRead)
def create_user_goal(
    user_goal: UserGoalCreate, db_session: Annotated[DBSession, Depends(get_db_session)]
) -> UserGoal:
    """
    Create a new user-goal relationship.
    """
    # Validate foreign keys
    user = db_session.get(UserProfile, user_goal.user_id)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    # Create the user-goal relationship
    db_user_goal = UserGoal(**user_goal.dict())
    db_session.add(db_user_goal)
    db_session.commit()
    db_session.refresh(db_user_goal)
    return db_user_goal


@router.get('/{user_id}', response_model=list[str])
def get_user_goals(
    user_id: UUID, db_session: Annotated[DBSession, Depends(get_db_session)]
) -> list[str]:
    """
    Retrieve all goals associated with a specific user.
    """
    user = db_session.get(UserProfile, user_id)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    statement = select(UserGoal).where(UserGoal.user_id == user_id)
    user_goals = db_session.exec(statement).all()
    return [ug.goal for ug in user_goals]
