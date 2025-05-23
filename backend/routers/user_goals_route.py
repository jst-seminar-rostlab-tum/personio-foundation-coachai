from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..models.goal import Goal, GoalRead
from ..models.user_goal import UserGoal, UserGoalCreate, UserGoalRead
from ..models.user_profile_model import UserProfileModel

router = APIRouter(prefix='/user-goals', tags=['User Goals'])


@router.post('/', response_model=UserGoalRead)
def create_user_goal(
    user_goal: UserGoalCreate, session: Annotated[Session, Depends(get_session)]
) -> UserGoal:
    """
    Create a new user-goal relationship.
    """
    # Validate foreign keys
    goal = session.get(Goal, user_goal.goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail='Goal not found')

    user = session.get(UserProfileModel, user_goal.user_id)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    # Create the user-goal relationship
    db_user_goal = UserGoal(**user_goal.dict())
    session.add(db_user_goal)
    session.commit()
    session.refresh(db_user_goal)
    return db_user_goal


@router.get('/{user_id}', response_model=list[GoalRead])
def get_user_goals(user_id: UUID, session: Annotated[Session, Depends(get_session)]) -> list[Goal]:
    """
    Retrieve all goals associated with a specific user.
    """
    # Validate that the user exists
    user = session.get(UserProfileModel, user_id)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    # Fetch all user-goal relationships for the user
    statement = select(UserGoal).where(UserGoal.user_id == user_id)
    user_goals = session.exec(statement).all()

    # Fetch the associated goals
    goal_ids = [user_goal.goal_id for user_goal in user_goals]
    statement = select(Goal).where(Goal.id.is_in(goal_ids))
    goals = session.exec(statement).all()

    return list(goals)
