from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session as DBSession
from sqlmodel import select

from app.database import get_db_session
from app.models.session import Session
from app.models.session_turn import (
    SessionTurn,
    SessionTurnCreate,
    SessionTurnRead,
)

router = APIRouter(prefix='/session-turns', tags=['Session Turns'])


@router.get('/', response_model=list[SessionTurnRead])
def get_session_turns(
    db_session: Annotated[DBSession, Depends(get_db_session)],
) -> list[SessionTurn]:
    """
    Retrieve all session turns.
    """
    statement = select(SessionTurn)
    turns = db_session.exec(statement).all()
    return list(turns)


@router.post('/', response_model=SessionTurnRead)
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


@router.put('/{turn_id}', response_model=SessionTurnRead)
def update_session_turn(
    turn_id: UUID,
    updated_data: SessionTurnCreate,
    db_session: Annotated[DBSession, Depends(get_db_session)],
) -> SessionTurn:
    """
    Update an existing session turn.
    """
    turn = db_session.get(SessionTurn, turn_id)
    if not turn:
        raise HTTPException(status_code=404, detail='Session turn not found')

    # Validate foreign key
    if updated_data.session_id:
        session = db_session.get(Session, updated_data.session_id)
        if not session:
            raise HTTPException(status_code=404, detail='Session not found')

    for key, value in updated_data.dict().items():
        setattr(turn, key, value)

    db_session.add(turn)
    db_session.commit()
    db_session.refresh(turn)
    return turn


@router.delete('/{turn_id}', response_model=dict)
def delete_session_turn(
    turn_id: UUID, db_session: Annotated[DBSession, Depends(get_db_session)]
) -> dict:
    """
    Delete a session turn.
    """
    turn = db_session.get(SessionTurn, turn_id)
    if not turn:
        raise HTTPException(status_code=404, detail='Session turn not found')

    db_session.delete(turn)
    db_session.commit()
    return {'message': 'Session turn deleted successfully'}
