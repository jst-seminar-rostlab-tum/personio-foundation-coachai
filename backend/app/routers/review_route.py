from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session as DBSession

from app.database import get_db_session
from app.dependencies import require_admin, require_user
from app.models.conversation_scenario import ConversationScenario
from app.models.review import Review
from app.models.session import Session
from app.models.user_profile import AccountRole, UserProfile
from app.schemas.review import (
    PaginatedReviewsResponse,
    ReviewCreate,
    ReviewRead,
    ReviewResponse,
)
from app.services.review_service import ReviewService

router = APIRouter(prefix='/review', tags=['User Review'])


def get_review_service(db: Annotated[DBSession, Depends(get_db_session)]) -> ReviewService:
    return ReviewService(db)


@router.get(
    '',
    response_model=list[ReviewRead] | PaginatedReviewsResponse,
    dependencies=[Depends(require_admin)],
)
def get_reviews(
    service: Annotated[ReviewService, Depends(get_review_service)],
    limit: int | None = Query(None),
    page: int | None = Query(None),
    page_size: int = Query(10),
    sort: str = Query('newest'),
) -> list[ReviewRead] | PaginatedReviewsResponse:
    """
    Retrieve user reviews with optional pagination, statistics and sorting.
    """
    return service.get_reviews(limit, page, page_size, sort)


@router.post('', response_model=ReviewResponse)
def create_review(
    review: ReviewCreate,
    db_session: Annotated[DBSession, Depends(get_db_session)],
    user_profile: Annotated[UserProfile, Depends(require_user)],
) -> ReviewResponse:
    """
    Create a new review.
    """
    user_id = user_profile.id  # Logged-in user's ID

    if review.session_id is not None:
        # Review is for a session --> without a session_id, it is a general review

        # Check if the session exists
        session = db_session.get(Session, review.session_id)
        if not session:
            raise HTTPException(status_code=404, detail='Session not found')

        # Check if the review is for a session of the logged-in user or the user is an admin
        # For this, we need to check the conversation scenario of the session
        conversation_scenario = db_session.get(ConversationScenario, session.scenario_id)
        if not conversation_scenario:
            raise HTTPException(
                status_code=404, detail='No conversation scenario found for the session'
            )
        if (
            conversation_scenario.user_id != user_id
            and user_profile.account_role != AccountRole.admin
        ):
            raise HTTPException(
                status_code=403,
                detail='Not your session: You do not have permission to create this review.',
            )

    if review.rating < 1 or review.rating > 5:
        raise HTTPException(status_code=400, detail='Rating must be between 1 and 5')

    new_review = Review(
        user_id=user_id,
        session_id=review.session_id,
        rating=review.rating,
        comment=review.comment,
    )
    db_session.add(new_review)
    db_session.commit()
    db_session.refresh(new_review)

    return ReviewResponse(
        message='Review submitted successfully',
        review_id=new_review.id,
    )
