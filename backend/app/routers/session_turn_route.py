from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session as DBSession

from app.database import get_db_session
from app.models.session import Session
from app.models.session_turn import SessionTurn
from app.schemas.session_turn import (
    SessionTurnCreate,
    SessionTurnRead,
)

router = APIRouter(prefix='/session-turns', tags=['Session Turns'])


@router.post('', response_model=SessionTurnRead)
def create_session_turn(
    turn: SessionTurnCreate, db_session: Annotated[DBSession, Depends(get_db_session)]
) -> SessionTurn:
    """
    Create a new session turn.
    """
    # Validate foreign key
    session = db_session.get(Session, turn.session_id)
    if not session:
        raise HTTPException(status_code=404, detail='Session not found')

    new_turn = SessionTurn(**turn.dict())
    db_session.add(new_turn)
    db_session.commit()
    db_session.refresh(new_turn)
    return new_turn
