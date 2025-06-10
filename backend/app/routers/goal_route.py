from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session as DBSession
from sqlmodel import select

from app.database import get_db_session
from app.models.goal import Goal, GoalCreate, GoalRead

router = APIRouter(prefix='/goals', tags=['Goals'])


@router.get('/', response_model=list[GoalRead])
def get_goals(db_session: Annotated[DBSession, Depends(get_db_session)]) -> list[Goal]:
    """
    Retrieve all goals.
    """
    statement = select(Goal)
    goals = db_session.exec(statement).all()
    return list(goals)


@router.post('/', response_model=GoalRead)
def create_goal(
    goal: GoalCreate, db_session: Annotated[DBSession, Depends(get_db_session)]
) -> Goal:
    """
    Create a new goal.
    """
    db_goal = Goal(**goal.dict())
    db_session.add(db_goal)
    db_session.commit()
    db_session.refresh(db_goal)
    return db_goal
