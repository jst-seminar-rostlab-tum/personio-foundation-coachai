from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..models.language import Language
from ..models.training_case import TrainingCase
from ..models.training_session import (
    TrainingSession,
    TrainingSessionCreate,
    TrainingSessionRead,
)
from ..models.training_session_feedback import (
    TrainingSessionFeedback,
    TrainingSessionFeedbackRead,
)

router = APIRouter(prefix='/training-session', tags=['Training Sessions'])


@router.get('/', response_model=list[TrainingSessionRead])
def get_training_sessions(
    session: Annotated[Session, Depends(get_session)],
) -> list[TrainingSession]:
    """
    Retrieve all training sessions.
    """
    statement = select(TrainingSession)
    sessions = session.exec(statement).all()
    return list(sessions)


@router.post('/', response_model=TrainingSessionRead)
def create_training_session(
    session_data: TrainingSessionCreate, session: Annotated[Session, Depends(get_session)]
) -> TrainingSession:
    """
    Create a new training session.
    """
    # Validate foreign keys
    case = session.get(TrainingCase, session_data.case_id)
    if not case:
        raise HTTPException(status_code=404, detail='Training case not found')

    language = session.exec(
        select(Language).where(Language.code == session_data.language_code)
    ).first()
    if not language:
        raise HTTPException(status_code=404, detail='Language not found')

    db_session = TrainingSession(**session_data.dict())
    session.add(db_session)
    session.commit()
    session.refresh(db_session)
    return db_session


@router.put('/{session_id}', response_model=TrainingSessionRead)
def update_training_session(
    session_id: UUID,
    updated_data: TrainingSessionCreate,
    session: Annotated[Session, Depends(get_session)],
) -> TrainingSession:
    """
    Update an existing training session.
    """
    training_session = session.get(TrainingSession, session_id)
    if not training_session:
        raise HTTPException(status_code=404, detail='Training session not found')

    # Validate foreign keys
    if updated_data.case_id:
        case = session.get(TrainingCase, updated_data.case_id)
        if not case:
            raise HTTPException(status_code=404, detail='Training case not found')

    if updated_data.language_code:
        language = session.exec(
            select(Language).where(Language.code == updated_data.language_code)
        ).first()
        if not language:
            raise HTTPException(status_code=404, detail='Language not found')

    for key, value in updated_data.dict().items():
        setattr(training_session, key, value)

    session.add(training_session)
    session.commit()
    session.refresh(training_session)
    return training_session


@router.delete('/{session_id}', response_model=dict)
def delete_training_session(
    session_id: UUID, session: Annotated[Session, Depends(get_session)]
) -> dict:
    """
    Delete a training session.
    """
    training_session = session.get(TrainingSession, session_id)
    if not training_session:
        raise HTTPException(status_code=404, detail='Training session not found')

    session.delete(training_session)
    session.commit()
    return {'message': 'Training session deleted successfully'}


@router.get('/{id_training_session}/feedback', response_model=TrainingSessionFeedbackRead)
def get_training_session_feedback(
    id_training_session: UUID, session: Annotated[Session, Depends(get_session)]
) -> TrainingSessionFeedback:
    """
    Retrieve the training session feedback for a given training session ID.
    """
    # Validate that the training session exists
    training_session = session.get(TrainingSession, id_training_session)
    if not training_session:
        raise HTTPException(status_code=404, detail='Training session not found')

    # Fetch the associated training session feedback
    statement = select(TrainingSessionFeedback).where(
        TrainingSessionFeedback.session_id == id_training_session
    )
    training_session_feedback = session.exec(statement).first()

    if not training_session_feedback:
        raise HTTPException(status_code=404, detail='Training session feedback not found')

    return training_session_feedback
