from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.models.user_feedback import (
    UserFeedback,
    UserFeedbackCreate,
    UserFeedbackRead,
    UserFeedbackResponse,
)
from app.models.user_profile import UserProfile

router = APIRouter(prefix='/feedback', tags=['User Feedback'])


@router.get('/', response_model=list[UserFeedbackRead])
def get_user_feedbacks(session: Annotated[Session, Depends(get_session)]) -> list[UserFeedback]:
    """
    Retrieve all user feedbacks.
    """
    statement = select(UserFeedback)
    user_feedbacks = session.exec(statement).all()
    return list(user_feedbacks)


@router.post('/', response_model=UserFeedbackResponse)
def create_user_feedback(
    user_feedback: UserFeedbackCreate, session: Annotated[Session, Depends(get_session)]
) -> UserFeedbackResponse:
    """
    Create a new user feedback.
    """
    user = session.get(UserProfile, user_feedback.user_id)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    db_feedback = UserFeedback(**user_feedback.dict())
    session.add(db_feedback)
    session.commit()
    session.refresh(db_feedback)

    return UserFeedbackResponse(
        message='Feedback submitted successfully',
        feedback_id=db_feedback.id,
    )
