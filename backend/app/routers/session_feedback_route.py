from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session as DBSession
from sqlmodel import select

from app.database import get_db_session
from app.models.session import Session
from app.models.session_feedback import (
    FeedbackStatusEnum,
    SessionFeedback,
    SessionFeedbackCreate,
    SessionFeedbackRead,
)

router = APIRouter(prefix='/session-feedback', tags=['Session Feedback'])


@router.get('/', response_model=list[SessionFeedbackRead])
def get_session_feedbacks(
    db_session: Annotated[DBSession, Depends(get_db_session)],
) -> list[SessionFeedback]:
    """
    Retrieve all session feedbacks.
    """
    statement = select(SessionFeedback)
    feedbacks = db_session.exec(statement).all()
    return list(feedbacks)


@router.post('/', response_model=SessionFeedbackRead)
def create_session_feedback(
    feedback: SessionFeedbackCreate, db_session: Annotated[DBSession, Depends(get_db_session)]
) -> SessionFeedback:
    """
    Create a new Session feedback.
    """
    # Validate foreign key
    session = db_session.get(Session, feedback.session_id)
    if not session:
        raise HTTPException(status_code=404, detail='Session not found')

    new_feedback = SessionFeedback(**feedback.dict())
    db_session.add(new_feedback)
    db_session.commit()
    db_session.refresh(new_feedback)
    return new_feedback


@router.get('/{feedback_id}', response_model=SessionFeedbackRead)
def get_session_feedback(
    feedback_id: UUID, db_session: Annotated[DBSession, Depends(get_db_session)]
) -> SessionFeedbackRead:
    """
    Retrieve a specific session feedback by ID.
    """
    feedback = db_session.get(SessionFeedback, feedback_id)

    if not feedback:
        raise HTTPException(status_code=404, detail='Session feedback not found')

    if feedback.status == FeedbackStatusEnum.pending:
        raise HTTPException(status_code=202, detail='Session feedback in progress.')

    elif feedback.status == FeedbackStatusEnum.failed:
        raise HTTPException(status_code=500, detail='Session feedback failed.')

    return feedback


@router.put('/{feedback_id}', response_model=SessionFeedbackRead)
def update_session_feedback(
    feedback_id: UUID,
    updated_data: dict,
    db_session: Annotated[DBSession, Depends(get_db_session)],
) -> SessionFeedback:
    """
    Update an existing session feedback.
    """
    feedback = db_session.get(SessionFeedback, feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail='Session feedback not found')

    for key, value in updated_data.items():
        if hasattr(feedback, key):  # Ensure the field exists in the model
            setattr(
                feedback,
                key,
                value if value is not None else getattr(SessionFeedback, key).default,
            )
    db_session.add(feedback)
    db_session.commit()
    db_session.refresh(feedback)
    return feedback


@router.delete('/{feedback_id}', response_model=dict)
def delete_session_feedback(
    feedback_id: UUID, db_session: Annotated[DBSession, Depends(get_db_session)]
) -> dict:
    """
    Delete a session feedback.
    """
    feedback = db_session.get(SessionFeedback, feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail='Session feedback not found')

    db_session.delete(feedback)
    db_session.commit()
    return {'message': 'Session feedback deleted successfully'}
