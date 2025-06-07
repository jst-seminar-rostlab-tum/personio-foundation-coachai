from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.database import get_session
from app.models.goal import Goal, GoalCreate, GoalRead

router = APIRouter(prefix='/goals', tags=['Goals'])


@router.get('/', response_model=list[GoalRead])
def get_goals(session: Annotated[Session, Depends(get_session)],
              lang: str = Query(default="en",
                                description="Requested language code (e.g. 'en', 'de')")) \
        -> list[Goal]:
    """
       Retrieve all goals with language fallback (preferring requested language).
    """

    # select goals in the requested language or fallback to English
    statement = select(Goal).where(Goal.language_code.in_([lang, "en"]))
    results = session.exec(statement).all()

    # Create a dictionary to hold goals by ID, preferring the requested language
    goals_by_id = {}
    for goal in results:
        if goal.id not in goals_by_id or goal.language_code == lang:
            goals_by_id[goal.id] = goal

    return list(goals_by_id.values())


@router.post('/', response_model=GoalRead)
def create_goal(goal: GoalCreate, session: Annotated[Session, Depends(get_session)]) -> Goal:
    """
    Create a new goal.
    """
    goal_id = goal.id or uuid4()
    lang_code = goal.language_code or "en"

    if lang_code not in ["en", "de"]:
        raise HTTPException(status_code=400, detail="Language code must be 'en' or 'de'.")

    # Check if a goal with the same ID and language already exists
    stmt = select(Goal).where(
        Goal.id == goal_id,
        Goal.language_code == lang_code
    )

    existing = session.exec(stmt).first()
    if existing:
        raise HTTPException(status_code=400, detail="Goal with this language already exists.")

    db_goal = Goal(
        id=goal_id,
        language_code=lang_code,
        label=goal.label,
        description=goal.description
    )

    session.add(db_goal)
    session.commit()
    session.refresh(db_goal)
    return db_goal
