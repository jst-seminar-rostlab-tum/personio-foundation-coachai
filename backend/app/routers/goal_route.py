from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.database import get_session
from app.models.goal import Goal, GoalCreate, GoalRead

router = APIRouter(prefix='/goals', tags=['Goals'])


@router.get('/', response_model=list[GoalRead])
def get_goals(session: Annotated[Session, Depends(get_session)]) -> list[Goal]:
    """
    Retrieve all goals.
    """
    statement = select(Goal)
    goals = session.exec(statement).all()
    return list(goals)


@router.post('/', response_model=GoalRead)
def create_goal(goal: GoalCreate, session: Annotated[Session, Depends(get_session)]) -> Goal:
    """
    Create a new goal.
    """
    db_goal = Goal(**goal.dict())
    session.add(db_goal)
    session.commit()
    session.refresh(db_goal)
    return db_goal
