from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session as DBSession
from sqlmodel import select

from app.database import get_session
from app.models.app_review import (
    Review,
    ReviewCreate,
    ReviewRead,
    ReviewResponse,
)
from app.models.user_profile import UserProfile

router = APIRouter(prefix='/review', tags=['User Review'])


@router.get('/', response_model=list[ReviewRead])
def get_reviews(db_session: Annotated[DBSession, Depends(get_session)]) -> list[Review]:
    """
    Retrieve all reviews.
    """
    statement = select(Review)
    reviews = db_session.exec(statement).all()
    return list(reviews)


@router.post('/', response_model=ReviewResponse)
def create_review(
    review: ReviewCreate, db_session: Annotated[DBSession, Depends(get_session)]
) -> ReviewResponse:
    """
    Create a new review.
    """
    user = db_session.get(UserProfile, review.user_id)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    new_review = Review(**review.dict())
    db_session.add(new_review)
    db_session.commit()
    db_session.refresh(new_review)

    return ReviewResponse(
        message='Review submitted successfully',
        review_id=new_review.id,
    )
