from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, asc, desc, select

from ..database import get_session
from ..models.reviews import PaginatedReviewsResponse, ReviewItem
from ..models.user_feedback import UserFeedback
from ..models.user_profile import UserProfile

router = APIRouter(prefix='/reviews', tags=['Reviews'])


@router.get('/', response_model=list[ReviewItem] | PaginatedReviewsResponse)
def get_reviews(
    session: Annotated[Session, Depends(get_session)],
    limit: Optional[int] = Query(None),
    page: Optional[int] = Query(None),
    page_size: int = Query(10),
    sort: str = Query('newest'),
) -> list[ReviewItem] | PaginatedReviewsResponse:
    """
    Retrieve user reviews with optional pagination and sorting.
    """

    # Getting user feedbacks from the database
    sort_mapping = {
        'newest': desc(UserFeedback.created_at),
        'oldest': asc(UserFeedback.created_at),
        'highest': desc(UserFeedback.rating),
        'lowest': asc(UserFeedback.rating),
    }

    order_by = sort_mapping.get(sort, desc(UserFeedback.created_at))
    statement = select(UserFeedback).order_by(order_by)

    if limit is not None:
        statement = statement.limit(limit)
        feedbacks = session.exec(statement).all()

        # Getting the user profiles for the reviews to get user names
        if not feedbacks:
            return []
        user_ids = [feedback.user_id for feedback in feedbacks]
        user_profiles = session.exec(select(UserProfile).where(UserProfile.id.in_(user_ids))).all()

        user_profiles_dict = {profile.id: profile for profile in user_profiles}

        # Constructing the review items
        reviews = []
        for feedback in feedbacks:
            user_profile = user_profiles_dict.get(feedback.user_id)
            if user_profile:
                reviews.append(
                    ReviewItem(
                        id=feedback.id,
                        user_name=user_profile.user_name,
                        rating=feedback.rating,
                        comment=feedback.comment,
                        date=feedback.created_at.date(),
                    )
                )
        return reviews

    # For pagination
    total_count = len(session.exec(select(UserFeedback)).all())
    total_pages = (total_count + page_size - 1) // page_size
    offset = (page - 1) * page_size if page else 0

    statement = statement.offset(offset).limit(page_size)
    feedbacks = session.exec(statement).all()

    # Getting the user profiles for the reviews to get user names
    if not feedbacks:
        return []
    user_ids = [feedback.user_id for feedback in feedbacks]
    user_profiles = session.exec(select(UserProfile).where(UserProfile.id.in_(user_ids))).all()

    user_profiles_dict = {profile.id: profile for profile in user_profiles}

    # Constructing the review items
    reviews = []
    for feedback in feedbacks:
        user_profile = user_profiles_dict.get(feedback.user_id)
        if user_profile:
            reviews.append(
                ReviewItem(
                    id=feedback.id,
                    user_name=user_profile.user_name,
                    rating=feedback.rating,
                    comment=feedback.comment,
                    date=feedback.created_at.date(),
                )
            )

    return PaginatedReviewsResponse(
        reviews=reviews,
        pagination={
            'currentPage': page,
            'totalPages': total_pages,
            'totalCount': total_count,
        },
    )
