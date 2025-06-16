from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session as DBSession
from sqlmodel import asc, desc, select

from app.database import get_db_session
from app.dependencies import require_admin, require_user
from app.models.conversation_scenario import ConversationScenario
from app.models.review import (
    PaginatedReviewsResponse,
    Review,
    ReviewCreate,
    ReviewRead,
    ReviewResponse,
    ReviewStatistics,
)
from app.models.session import Session
from app.models.user_profile import AccountRole, UserProfile

router = APIRouter(prefix='/review', tags=['User Review'])


@router.get(
    '',
    response_model=list[ReviewRead] | PaginatedReviewsResponse,
    dependencies=[Depends(require_admin)],
)
def get_reviews(
    db_session: Annotated[DBSession, Depends(get_db_session)],
    limit: Optional[int] = Query(None),
    page: Optional[int] = Query(None),
    page_size: int = Query(10),
    sort: str = Query('newest'),
) -> list[ReviewRead] | PaginatedReviewsResponse:
    """
    Retrieve user reviews with optional pagination, statistics and sorting.
    """
    # Getting reviews from the database
    sort_mapping = {
        'newest': desc(Review.created_at),
        'oldest': asc(Review.created_at),
        'highest': desc(Review.rating),
        'lowest': asc(Review.rating),
    }

    order_by = sort_mapping.get(sort, desc(Review.created_at))
    statement = select(Review).order_by(order_by)

    if limit is not None:
        statement = statement.limit(limit)
        reviews = db_session.exec(statement).all()
    else:
        # Pagination
        total_count = len(db_session.exec(select(Review)).all())
        total_pages = (total_count + page_size - 1) // page_size
        offset = (page - 1) * page_size if page else 0

        statement = statement.offset(offset).limit(page_size)
        reviews = db_session.exec(statement).all()

    if not reviews:
        return []

    # Getting the user profiles for the reviews to get user names
    user_ids = [review.user_id for review in reviews]
    user_profiles = db_session.exec(select(UserProfile).where(UserProfile.id.in_(user_ids))).all()
    user_profiles_dict = {profile.id: profile for profile in user_profiles}

    # Constructing the review items
    review_list = []
    for review in reviews:
        user_profile = user_profiles_dict.get(review.user_id)
        if user_profile:
            review_list.append(
                ReviewRead(
                    id=review.id,
                    user_id=review.user_id,
                    session_id=review.session_id,
                    rating=review.rating,
                    comment=review.comment,
                    date=review.created_at.date(),
                )
            )

    if limit is not None:
        return review_list

    return PaginatedReviewsResponse(
        reviews=review_list,
        pagination={
            'currentPage': page if page else 1,
            'totalPages': total_pages,
            'totalCount': total_count,
        },
        rating_statistics=ReviewStatistics(
            average=round(sum(review.rating for review in reviews) / len(reviews), 2),
            num_five_star=sum(1 for review in reviews if review.rating == 5),
            num_four_star=sum(1 for review in reviews if review.rating == 4),
            num_three_star=sum(1 for review in reviews if review.rating == 3),
            num_two_star=sum(1 for review in reviews if review.rating == 2),
            num_one_star=sum(1 for review in reviews if review.rating == 1),
        ),
    )


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
