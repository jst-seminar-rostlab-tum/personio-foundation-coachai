from collections.abc import Sequence
from uuid import UUID

from fastapi import HTTPException, Query
from sqlalchemy import func
from sqlmodel import Session as DBSession
from sqlmodel import asc, desc, select

from app.models.conversation_scenario import ConversationScenario
from app.models.review import Review
from app.models.session import Session
from app.models.user_profile import AccountRole, UserProfile
from app.schemas.review import (
    PaginatedReviewsResponse,
    ReviewCreate,
    ReviewRead,
    ReviewResponse,
    ReviewStatistics,
)


class ReviewService:
    def __init__(self, db: DBSession) -> None:
        self.db = db

    def _get_user_profile(self, user_id: UUID) -> UserProfile:
        """
        Retrieve a user profile by user ID.
        """
        user_profile = self.db.exec(select(UserProfile).where(UserProfile.id == user_id)).first()
        if not user_profile:
            raise HTTPException(
                status_code=404,
                detail=f'User profile with ID {user_id} not found.',
            )
        return user_profile

    def _add_user_info_to_reviews(self, reviews: Sequence[Review]) -> list[ReviewRead]:
        """
        Add user information to a list of reviews.
        """
        review_list = []
        for review in reviews:
            user_profile = self._get_user_profile(review.user_id)
            if user_profile:
                review_list.append(
                    ReviewRead(
                        id=review.id,
                        user_id=review.user_id,
                        user_email=user_profile.email,
                        session_id=review.session_id,
                        rating=review.rating,
                        comment=review.comment,
                        date=review.created_at.date(),
                    )
                )
        return review_list

    def _get_limited_reviews(self, limit: int, sort: str = Query('newest')) -> list[ReviewRead]:
        """
        Retrieve a list of reviews with a limit.
        """
        sort_mapping = {
            'newest': desc(Review.created_at),
            'oldest': asc(Review.created_at),
            'highest': desc(Review.rating),
            'lowest': asc(Review.rating),
        }

        order_by = sort_mapping.get(sort, desc(Review.created_at))
        statement = select(Review).order_by(order_by).limit(limit)
        reviews = self.db.exec(statement).all()
        if not reviews:
            return []

        return self._add_user_info_to_reviews(reviews)

    def _get_paginated_reviews(
        self,
        page: int | None = Query(None),
        page_size: int = Query(10),
        sort: str = Query('newest'),
    ) -> PaginatedReviewsResponse:
        """Retrieve paginated reviews with optional sorting."""

        sort_mapping = {
            'newest': desc(Review.created_at),
            'oldest': asc(Review.created_at),
            'highest': desc(Review.rating),
            'lowest': asc(Review.rating),
        }

        order_by = sort_mapping.get(sort, desc(Review.created_at))
        statement = select(Review).order_by(order_by)

        # Pagination
        total_count = self.db.exec(select(func.count()).select_from(Review)).one()
        if total_count == 0:
            return PaginatedReviewsResponse(
                reviews=[],
                pagination={
                    'currentPage': page if page else 1,
                    'totalPages': 0,
                    'totalCount': 0,
                    'pageSize': page_size,
                },
                rating_statistics=ReviewStatistics(
                    average=0.0,
                    num_five_star=0,
                    num_four_star=0,
                    num_three_star=0,
                    num_two_star=0,
                    num_one_star=0,
                ),
            )

        total_pages = (total_count + page_size - 1) // page_size
        offset = (page - 1) * page_size if page else 0

        statement = statement.offset(offset).limit(page_size)
        reviews = self.db.exec(statement).all()

        review_list = self._add_user_info_to_reviews(reviews)

        return PaginatedReviewsResponse(
            reviews=review_list,
            pagination={
                'currentPage': page if page else 1,
                'totalPages': total_pages,
                'totalCount': total_count,
                'pageSize': page_size,
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

    def get_reviews(
        self,
        limit: int | None = Query(None),
        page: int | None = Query(None),
        page_size: int = Query(10),
        sort: str = Query('newest'),
    ) -> list[ReviewRead] | PaginatedReviewsResponse:
        """
        Retrieve user reviews with optional pagination, statistics and sorting.
        """

        if limit is not None:
            return self._get_limited_reviews(limit, sort)

        else:
            return self._get_paginated_reviews(page, page_size, sort)

    def _check_session_review_permissions(
        self,
        session_id: UUID,
        user_profile: UserProfile,
    ) -> None:
        """
        Check if the user has permission to create a review for the given session.
        Raises HTTPException if the session does not exist or the user does not have permission.
        """
        # Check if the session exists
        session = self.db.get(Session, session_id)
        if not session:
            raise HTTPException(status_code=404, detail='Session not found')

        # Check if the review is for a session of the logged-in user or the user is an admin
        # For this, we need to check the conversation scenario of the session
        conversation_scenario = self.db.get(ConversationScenario, session.scenario_id)
        if not conversation_scenario:
            raise HTTPException(
                status_code=404, detail='No conversation scenario found for the session'
            )
        if (
            conversation_scenario.user_id != user_profile.id
            and user_profile.account_role != AccountRole.admin
        ):
            raise HTTPException(
                status_code=403,
                detail='Not your session: You do not have permission to create this review.',
            )

    def create_review(
        self,
        review: ReviewCreate,
        user_profile: UserProfile,
    ) -> ReviewResponse:
        """
        Create a new review.
        """
        user_id = user_profile.id  # Logged-in user's ID

        if review.session_id is not None:
            # Review is for a session --> without a session_id, it is a general review
            self._check_session_review_permissions(review.session_id, user_profile)

        if review.rating < 1 or review.rating > 5:
            raise HTTPException(status_code=400, detail='Rating must be between 1 and 5')

        new_review = Review(
            user_id=user_id,
            session_id=review.session_id,
            rating=review.rating,
            comment=review.comment,
        )
        self.db.add(new_review)
        self.db.commit()
        self.db.refresh(new_review)

        return ReviewResponse(
            message='Review submitted successfully',
            review_id=new_review.id,
        )
