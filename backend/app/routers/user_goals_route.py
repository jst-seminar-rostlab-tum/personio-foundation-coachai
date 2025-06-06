from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, col, select

from app.database import get_session
from app.models.goal import UUID, Goal, GoalRead
from app.models.user_goal import UserGoal, UserGoalCreate, UserGoalRead
from app.models.user_profile import UserProfile

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

    user = session.get(UserProfile, user_goal.user_id)
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
    user = session.get(UserProfile, user_id)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    # Fetch all user-goal relationships for the user
    statement = select(UserGoal).where(UserGoal.user_id == user_id)
    user_goals = session.exec(statement).all()

    goal_ids = [ug.goal_id for ug in user_goals]

    # If the user has no goals, avoid generating an empty IN () clause
    if not goal_ids:
        return []

    # Fetch the associated goals
    statement = select(Goal).where(col(Goal.id).in_(goal_ids))
    goals = session.exec(statement).all()
    return list(goals)
