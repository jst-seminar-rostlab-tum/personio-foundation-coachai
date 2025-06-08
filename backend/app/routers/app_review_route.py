from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.models.app_review import (
    AppReview,
    AppReviewCreate,
    AppReviewRead,
    AppReviewResponse,
)
from app.models.user_profile import UserProfile

router = APIRouter(prefix='/feedback', tags=['User Feedback'])


@router.get('/', response_model=list[AppReviewRead])
def get_app_reviews(session: Annotated[Session, Depends(get_session)]) -> list[AppReview]:
    """
    Retrieve all user feedbacks.
    """
    statement = select(AppReview)
    app_reviews = session.exec(statement).all()
    return list(app_reviews)


@router.post('/', response_model=AppReviewResponse)
def create_app_review(
    app_review: AppReviewCreate, session: Annotated[Session, Depends(get_session)]
) -> AppReviewResponse:
    """
    Create a new user feedback.
    """
    user = session.get(UserProfile, app_review.user_id)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    db_feedback = AppReview(**app_review.dict())
    session.add(db_feedback)
    session.commit()
    session.refresh(db_feedback)

    return AppReviewResponse(
        message='Feedback submitted successfully',
        feedback_id=db_feedback.id,
    )
