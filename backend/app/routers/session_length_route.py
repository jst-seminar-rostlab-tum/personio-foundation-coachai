from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.models.session_length import SessionLength, SessionLengthCreate, SessionLengthRead

router = APIRouter(prefix='/session-lengths', tags=['Session Lengths'])


@router.get('/', response_model=list[SessionLengthRead])
def get_session_lengths(session: Annotated[Session, Depends(get_session)]) -> list[SessionLength]:
    """
    Retrieve all session lengths.
    """
    statement = select(SessionLength)
    results = session.exec(statement).all()
    return list(results)


@router.post('/', response_model=SessionLengthRead)
def create_session_length(
    session_length: SessionLengthCreate, session: Annotated[Session, Depends(get_session)]
) -> SessionLength:
    """
    Create a new session length.
    """
    new_session_length = SessionLength(**session_length.dict())
    session.add(new_session_length)
    session.commit()
    session.refresh(new_session_length)
    return new_session_length


@router.put('/{session_length_id}', response_model=SessionLengthRead)
def update_session_length(
    session_length_id: UUID,
    updated_data: SessionLengthCreate,
    session: Annotated[Session, Depends(get_session)],
) -> SessionLength:
    """
    Update an existing session length.
    """
    session_length = session.get(SessionLength, session_length_id)
    if not session_length:
        raise HTTPException(status_code=404, detail='Session length not found')
    for key, value in updated_data.dict().items():
        setattr(session_length, key, value)
    session.add(session_length)
    session.commit()
    session.refresh(session_length)
    return session_length


@router.delete('/{session_length_id}', response_model=dict)
def delete_session_length(
    session_length_id: UUID, session: Annotated[Session, Depends(get_session)]
) -> dict:
    """
    Delete a session length.
    """
    session_length = session.get(SessionLength, session_length_id)
    if not session_length:
        raise HTTPException(status_code=404, detail='Session length not found')
    session.delete(session_length)
    session.commit()
    return {'message': 'Session length deleted successfully'}
