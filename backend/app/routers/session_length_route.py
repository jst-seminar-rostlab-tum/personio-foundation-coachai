from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session as DBSession
from sqlmodel import select

from app.database import get_db_session
from app.models.session_length import SessionLength, SessionLengthCreate, SessionLengthRead

router = APIRouter(prefix='/session-lengths', tags=['Session Lengths'])


@router.get('/', response_model=list[SessionLengthRead])
def get_session_lengths(
    db_session: Annotated[DBSession, Depends(get_db_session)],
) -> list[SessionLength]:
    """
    Retrieve all session lengths.
    """
    statement = select(SessionLength)
    results = db_session.exec(statement).all()
    return list(results)


@router.post('/', response_model=SessionLengthRead)
def create_session_length(
    session_length: SessionLengthCreate, db_session: Annotated[DBSession, Depends(get_db_session)]
) -> SessionLength:
    """
    Create a new session length.
    """
    new_session_length = SessionLength(**session_length.dict())
    db_session.add(new_session_length)
    db_session.commit()
    db_session.refresh(new_session_length)
    return new_session_length


@router.put('/{session_length_id}', response_model=SessionLengthRead)
def update_session_length(
    session_length_id: UUID,
    updated_data: SessionLengthCreate,
    db_session: Annotated[DBSession, Depends(get_db_session)],
) -> SessionLength:
    """
    Update an existing session length.
    """
    session_length = db_session.get(SessionLength, session_length_id)
    if not session_length:
        raise HTTPException(status_code=404, detail='Session length not found')
    for key, value in updated_data.dict().items():
        setattr(session_length, key, value)
    db_session.add(session_length)
    db_session.commit()
    db_session.refresh(session_length)
    return session_length


@router.delete('/{session_length_id}', response_model=dict)
def delete_session_length(
    session_length_id: UUID, db_session: Annotated[DBSession, Depends(get_db_session)]
) -> dict:
    """
    Delete a session length.
    """
    session_length = db_session.get(SessionLength, session_length_id)
    if not session_length:
        raise HTTPException(status_code=404, detail='Session length not found')
    db_session.delete(session_length)
    db_session.commit()
    return {'message': 'Session length deleted successfully'}
