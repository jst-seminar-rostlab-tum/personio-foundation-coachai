from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session as DBSession

from app.database import get_db_session
from app.dependencies import require_admin, require_user
from app.models.user_profile import UserProfile
from app.schemas.review import (
    PaginatedReviewRead,
    ReviewConfirm,
    ReviewCreate,
    ReviewRead,
)
from app.services.review_service import ReviewService

router = APIRouter(prefix='/reviews', tags=['User Review'])


def get_review_service(db: Annotated[DBSession, Depends(get_db_session)]) -> ReviewService:
    return ReviewService(db)


@router.get(
    '',
    response_model=list[ReviewRead] | PaginatedReviewRead,
    dependencies=[Depends(require_admin)],
)
def get_reviews(
    service: Annotated[ReviewService, Depends(get_review_service)],
    limit: int | None = Query(None),
    page: int | None = Query(None),
    page_size: int = Query(10),
    sort: str = Query('newest'),
) -> list[ReviewRead] | PaginatedReviewRead:
    """
    Retrieve user reviews with optional pagination, statistics and sorting.
    """
    return service.get_reviews(limit, page, page_size, sort)


@router.post('', response_model=ReviewConfirm)
def create_review(
    review: ReviewCreate,
    user_profile: Annotated[UserProfile, Depends(require_user)],
    service: Annotated[ReviewService, Depends(get_review_service)],
) -> ReviewConfirm:
    """
    Create a new review.
    """
    return service.create_review(review, user_profile)
