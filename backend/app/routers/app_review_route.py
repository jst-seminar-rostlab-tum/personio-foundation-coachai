from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, asc, desc, select

from app.database import get_session
from app.models.app_review import (
    AppReview,
    AppReviewCreate,
    AppReviewRead,
    AppReviewResponse,
    PaginatedReviewsResponse,
)
from app.models.user_profile import UserProfile

router = APIRouter(prefix='/app-review', tags=['User App Review'])


@router.get('/', response_model=list[AppReviewRead] | PaginatedReviewsResponse)
def get_app_reviews(
    session: Annotated[Session, Depends(get_session)],
    limit: Optional[int] = Query(None),
    page: Optional[int] = Query(None),
    page_size: int = Query(10),
    sort: str = Query('newest'),
) -> list[AppReviewRead] | PaginatedReviewsResponse:
    """
    Retrieve user app reviews with optional pagination and sorting.
    """

    # Getting app reviews from the database
    sort_mapping = {
        'newest': desc(AppReview.created_at),
        'oldest': asc(AppReview.created_at),
        'highest': desc(AppReview.rating),
        'lowest': asc(AppReview.rating),
    }

    order_by = sort_mapping.get(sort, desc(AppReview.created_at))
    statement = select(AppReview).order_by(order_by)

    if limit is not None:
        statement = statement.limit(limit)
        app_reviews = session.exec(statement).all()
    else:
        # Pagination
        total_count = len(session.exec(select(AppReview)).all())
        total_pages = (total_count + page_size - 1) // page_size
        offset = (page - 1) * page_size if page else 0

        statement = statement.offset(offset).limit(page_size)
        app_reviews = session.exec(statement).all()

    if not app_reviews:
        return []

    # Getting the user profiles for the reviews to get user names
    user_ids = [app_review.user_id for app_review in app_reviews]
    user_profiles = session.exec(select(UserProfile).where(UserProfile.id.in_(user_ids))).all()
    user_profiles_dict = {profile.id: profile for profile in user_profiles}

    # Constructing the review items
    reviews = []
    for app_review in app_reviews:
        user_profile = user_profiles_dict.get(app_review.user_id)
        if user_profile:
            reviews.append(
                AppReviewRead(
                    id=app_review.id,
                    user_id=app_review.user_id,
                    rating=app_review.rating,
                    comment=app_review.comment,
                    date=app_review.created_at.date(),
                )
            )

    if limit is not None:
        return reviews

    return PaginatedReviewsResponse(
        reviews=reviews,
        pagination={
            'currentPage': page if page else 1,
            'totalPages': total_pages,
            'totalCount': total_count,
        },
    )


@router.post('/', response_model=AppReviewResponse)
def create_app_review(
    app_review: AppReviewCreate, session: Annotated[Session, Depends(get_session)]
) -> AppReviewResponse:
    """
    Create a new app review.
    """
    user = session.get(UserProfile, app_review.user_id)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    db_app_review = AppReview(**app_review.dict())
    session.add(db_app_review)
    session.commit()
    session.refresh(db_app_review)

    return AppReviewResponse(
        message='Feedback submitted successfully',
        app_review_id=db_app_review.id,
    )
