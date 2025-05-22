from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..models.training_session import TrainingSession
from ..models.training_session_feedback import (
    TrainingSessionFeedback,
    TrainingSessionFeedbackCreate,
    TrainingSessionFeedbackRead,
)

router = APIRouter(prefix='/training-session-feedback', tags=['Training Session Feedback'])


@router.get('/', response_model=list[TrainingSessionFeedbackRead])
def get_training_session_feedbacks(
    session: Annotated[Session, Depends(get_session)],
) -> list[TrainingSessionFeedback]:
    """
    Retrieve all training session feedbacks.
    """
    statement = select(TrainingSessionFeedback)
    feedbacks = session.exec(statement).all()
    return list(feedbacks)


@router.post('/', response_model=TrainingSessionFeedbackRead)
def create_training_session_feedback(
    feedback: TrainingSessionFeedbackCreate, session: Annotated[Session, Depends(get_session)]
) -> TrainingSessionFeedback:
    """
    Create a new training session feedback.
    """
    # Validate foreign key
    training_session = session.get(TrainingSession, feedback.session_id)
    if not training_session:
        raise HTTPException(status_code=404, detail='Training session not found')

    db_feedback = TrainingSessionFeedback(**feedback.dict())
    session.add(db_feedback)
    session.commit()
    session.refresh(db_feedback)
    return db_feedback


@router.put('/{feedback_id}', response_model=TrainingSessionFeedbackRead)
def update_training_session_feedback(
    feedback_id: UUID,
    updated_data: TrainingSessionFeedbackCreate,
    session: Annotated[Session, Depends(get_session)],
) -> TrainingSessionFeedback:
    """
    Update an existing training session feedback.
    """
    feedback = session.get(TrainingSessionFeedback, feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail='Training session feedback not found')

    # Validate foreign key
    if updated_data.session_id:
        training_session = session.get(TrainingSession, updated_data.session_id)
        if not training_session:
            raise HTTPException(status_code=404, detail='Training session not found')

    for key, value in updated_data.dict().items():
        setattr(feedback, key, value)

    session.add(feedback)
    session.commit()
    session.refresh(feedback)
    return feedback


@router.delete('/{feedback_id}', response_model=dict)
def delete_training_session_feedback(
    feedback_id: UUID, session: Annotated[Session, Depends(get_session)]
) -> dict:
    """
    Delete a training session feedback.
    """
    feedback = session.get(TrainingSessionFeedback, feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail='Training session feedback not found')

    session.delete(feedback)
    session.commit()
    return {'message': 'Training session feedback deleted successfully'}
