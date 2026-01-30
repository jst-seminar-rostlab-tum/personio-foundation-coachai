"""API routes for review route."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session as DBSession

from app.dependencies.auth import require_admin, require_user
from app.dependencies.database import get_db_session
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
    """Provide ReviewService via dependency injection.

    Parameters:
        db (DBSession): Database session dependency.

    Returns:
        ReviewService: Service instance.
    """
    return ReviewService(db)


@router.get(
    '',
    response_model=list[ReviewRead] | PaginatedReviewRead,
    dependencies=[Depends(require_admin)],
)
def get_reviews(
    service: Annotated[ReviewService, Depends(get_review_service)],
    page: int | None = Query(None),
    page_size: int = Query(8),
    sort: str = Query('newest'),
) -> list[ReviewRead] | PaginatedReviewRead:
    """Retrieve user reviews with optional pagination, statistics and sorting.

    Parameters:
        service (ReviewService): Service dependency.
        page (int | None): Page number (1-based).
        page_size (int): Items per page.
        sort (str): Sorting strategy.

    Returns:
        list[ReviewRead] | PaginatedReviewRead: Review payload(s).
    """
    return service.get_reviews(page, page_size, sort)


@router.post('', response_model=ReviewConfirm)
def create_review(
    review: ReviewCreate,
    user_profile: Annotated[UserProfile, Depends(require_user)],
    service: Annotated[ReviewService, Depends(get_review_service)],
) -> ReviewConfirm:
    """Create a new review.

    Parameters:
        review (ReviewCreate): Review payload.
        user_profile (UserProfile): Authenticated user profile.
        service (ReviewService): Service dependency.

    Returns:
        ReviewConfirm: Confirmation payload.
    """
    return service.create_review(review, user_profile)
