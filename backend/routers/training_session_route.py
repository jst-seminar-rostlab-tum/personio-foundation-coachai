from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..models.language_model import LanguageModel
from ..models.training_case_model import TrainingCaseModel
from ..models.training_session_model import (
    TrainingSessionCreate,
    TrainingSessionModel,
    TrainingSessionRead,
)

router = APIRouter(prefix='/training-sessions', tags=['Training Sessions'])


@router.get('/', response_model=list[TrainingSessionRead])
def get_training_sessions(
    session: Annotated[Session, Depends(get_session)],
) -> list[TrainingSessionModel]:
    """
    Retrieve all training sessions.
    """
    statement = select(TrainingSessionModel)
    sessions = session.exec(statement).all()
    return list(sessions)


@router.post('/', response_model=TrainingSessionRead)
def create_training_session(
    session_data: TrainingSessionCreate, session: Annotated[Session, Depends(get_session)]
) -> TrainingSessionModel:
    """
    Create a new training session.
    """
    # Validate foreign keys
    case = session.get(TrainingCaseModel, session_data.case_id)
    if not case:
        raise HTTPException(status_code=404, detail='Training case not found')

    language = session.exec(
        select(LanguageModel).where(LanguageModel.code == session_data.language_code)
    ).first()
    if not language:
        raise HTTPException(status_code=404, detail='Language not found')

    db_session = TrainingSessionModel(**session_data.dict())
    session.add(db_session)
    session.commit()
    session.refresh(db_session)
    return db_session


@router.put('/{session_id}', response_model=TrainingSessionRead)
def update_training_session(
    session_id: UUID,
    updated_data: TrainingSessionCreate,
    session: Annotated[Session, Depends(get_session)],
) -> TrainingSessionModel:
    """
    Update an existing training session.
    """
    training_session = session.get(TrainingSessionModel, session_id)
    if not training_session:
        raise HTTPException(status_code=404, detail='Training session not found')

    # Validate foreign keys
    if updated_data.case_id:
        case = session.get(TrainingCaseModel, updated_data.case_id)
        if not case:
            raise HTTPException(status_code=404, detail='Training case not found')

    if updated_data.language_code:
        language = session.exec(
            select(LanguageModel).where(LanguageModel.code == updated_data.language_code)
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
    training_session = session.get(TrainingSessionModel, session_id)
    if not training_session:
        raise HTTPException(status_code=404, detail='Training session not found')

    session.delete(training_session)
    session.commit()
    return {'message': 'Training session deleted successfully'}
