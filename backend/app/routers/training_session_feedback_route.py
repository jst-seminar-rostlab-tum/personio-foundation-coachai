from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session as DBSession
from sqlmodel import select

from app.database import get_session
from app.models.training_session import TrainingSession
from app.models.training_session_feedback import (
    FeedbackStatusEnum,
    TrainingSessionFeedback,
    TrainingSessionFeedbackCreate,
    TrainingSessionFeedbackRead,
)

router = APIRouter(prefix='/training-session-feedback', tags=['Training Session Feedback'])


@router.get('/', response_model=list[TrainingSessionFeedbackRead])
def get_training_session_feedbacks(
    db_session: Annotated[DBSession, Depends(get_session)],
) -> list[TrainingSessionFeedback]:
    """
    Retrieve all training session feedbacks.
    """
    statement = select(TrainingSessionFeedback)
    feedbacks = db_session.exec(statement).all()
    return list(feedbacks)


@router.post('/', response_model=TrainingSessionFeedbackRead)
def create_training_session_feedback(
    feedback: TrainingSessionFeedbackCreate, db_session: Annotated[DBSession, Depends(get_session)]
) -> TrainingSessionFeedback:
    """
    Create a new training session feedback.
    """
    # Validate foreign key
    training_session = db_session.get(TrainingSession, feedback.session_id)
    if not training_session:
        raise HTTPException(status_code=404, detail='Training session not found')

    db_feedback = TrainingSessionFeedback(**feedback.dict())
    db_session.add(db_feedback)
    db_session.commit()
    db_session.refresh(db_feedback)
    return db_feedback


@router.get('/{feedback_id}', response_model=TrainingSessionFeedbackRead)
def get_training_session_feedback(
    feedback_id: UUID, db_session: Annotated[DBSession, Depends(get_session)]
) -> TrainingSessionFeedbackRead:
    """
    Retrieve a specific training feedback by ID.
    """
    feedback = db_session.get(TrainingSessionFeedback, feedback_id)

    if not feedback:
        raise HTTPException(status_code=404, detail='Session feedback not found')

    if feedback.status == FeedbackStatusEnum.pending:
        raise HTTPException(status_code=202, detail='Session feedback in progress.')

    elif feedback.status == FeedbackStatusEnum.failed:
        raise HTTPException(status_code=500, detail='Session feedback failed.')

    return feedback


@router.put('/{feedback_id}', response_model=TrainingSessionFeedbackRead)
def update_training_session_feedback(
    feedback_id: UUID,
    updated_data: dict,
    db_session: Annotated[DBSession, Depends(get_session)],
) -> TrainingSessionFeedback:
    """
    Update an existing training session feedback.
    """
    feedback = db_session.get(TrainingSessionFeedback, feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail='Training session feedback not found')

    for key, value in updated_data.items():
        if hasattr(feedback, key):  # Ensure the field exists in the model
            setattr(
                feedback,
                key,
                value if value is not None else getattr(TrainingSessionFeedback, key).default,
            )
    db_session.add(feedback)
    db_session.commit()
    db_session.refresh(feedback)
    return feedback


@router.delete('/{feedback_id}', response_model=dict)
def delete_training_session_feedback(
    feedback_id: UUID, db_session: Annotated[DBSession, Depends(get_session)]
) -> dict:
    """
    Delete a training session feedback.
    """
    feedback = db_session.get(TrainingSessionFeedback, feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail='Training session feedback not found')

    db_session.delete(feedback)
    db_session.commit()
    return {'message': 'Training session feedback deleted successfully'}
