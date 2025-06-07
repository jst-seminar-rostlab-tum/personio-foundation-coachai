from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.database import get_session
from app.models.session_length import SessionLength, SessionLengthCreate, SessionLengthRead

router = APIRouter(prefix='/session-lengths', tags=['Session Lengths'])


@router.get('/', response_model=list[SessionLengthRead])
def get_session_lengths(session: Annotated[Session, Depends(get_session)],
                        lang: str = Query(default="en")) -> list[SessionLength]:
    """
    Retrieve all session lengths.
    """
    # select session_length in the requested language or fallback to English
    statement = select(SessionLength).where(SessionLength.language_code.in_([lang, "en"]))
    results = session.exec(statement).all()

    # Create a dictionary to hold session_length by ID, preferring the requested language
    session_lengths_by_id = {}
    for session_length in results:
        if session_length.id not in session_lengths_by_id or session_length.language_code == lang:
            session_lengths_by_id[session_length.id] = session_length

    return list(session_lengths_by_id.values())


@router.post('/', response_model=SessionLengthRead)
def create_session_length(
        session_length: SessionLengthCreate,
        session: Annotated[Session, Depends(get_session)]
) -> SessionLength:
    """
    Create a new session length.
    """
    session_length_id = session_length.id or uuid4()
    lang_code = session_length.language_code or "en"

    if lang_code not in ["en", "de"]:
        raise HTTPException(status_code=400, detail="Unsupported language code.")

    # Check if a session length with the same ID and language already exists
    stmt = select(SessionLength).where(
        SessionLength.id == session_length_id,
        SessionLength.language_code == lang_code
    )
    existing = session.exec(stmt).first()
    if existing:
        raise HTTPException(status_code=400,
                            detail="Session length with this language already exists.")

    new_session_length = SessionLength(
        id=session_length_id,
        language_code=lang_code,
        label=session_length.label,
        description=session_length.description,
        duration=session_length.duration
    )
    session.add(new_session_length)
    session.commit()
    session.refresh(new_session_length)
    return new_session_length


@router.put('/{session_length_id}', response_model=SessionLengthRead)
def update_session_length(
        session_length_id: UUID,
        updated_data: SessionLengthCreate,
        session: Annotated[Session, Depends(get_session)],
        lang: str = Query(default="en")
) -> SessionLength:
    """
    Update an existing session length.
    """
    stmt = select(SessionLength).where(
        SessionLength.id == session_length_id,
        SessionLength.language_code == updated_data.language_code or "en"
    )
    session_length = session.exec(stmt).first()

    if not session_length:
        raise HTTPException(status_code=404, detail='Session length not found')
    for key, value in updated_data.model_dump().items():
        if key != "id":
            setattr(session_length, key, value)
    session.add(session_length)
    session.commit()
    session.refresh(session_length)
    return session_length


@router.delete('/{session_length_id}', response_model=dict)
def delete_session_length(
        session_length_id: UUID, session: Annotated[Session, Depends(get_session)],
        lang: str = Query(default="en")
) -> dict:
    """
    Delete a session length.
    """
    stmt = select(SessionLength).where(
        SessionLength.id == session_length_id,
        SessionLength.language_code == lang
    )

    session_length = session.exec(stmt).first()
    if not session_length:
        raise HTTPException(status_code=404, detail='Session length not found')
    session.delete(session_length)
    session.commit()
    return {'message': 'Session length deleted successfully'}
