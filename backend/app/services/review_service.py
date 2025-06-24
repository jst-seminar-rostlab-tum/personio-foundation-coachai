from collections.abc import Sequence
from uuid import UUID

from fastapi import HTTPException, Query
from sqlalchemy import case, func
from sqlalchemy import select as sqlalchemy_select
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

    def _query_reviews_with_users(
        self,
        sort: str = Query('newest'),
        limit: int | None = None,
        offset: int | None = None,
    ) -> Sequence[tuple[Review, UserProfile]]:
        sort_mapping = {
            'newest': desc(Review.created_at),
            'oldest': asc(Review.created_at),
            'highest': desc(Review.rating),
            'lowest': asc(Review.rating),
        }

        order_by = sort_mapping.get(sort, desc(Review.created_at))

        stmt = (
            select(Review, UserProfile)
            .select_from(Review)
            .join(UserProfile, Review.user_id == UserProfile.id)  # type: ignore
            .order_by(order_by)
        )

        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)

        return self.db.exec(stmt).all()

    def _build_review_read_list(
        self, joined_reviews_users: Sequence[tuple[Review, UserProfile]]
    ) -> list[ReviewRead]:
        review_list = []
        for review, user in joined_reviews_users:
            review_list.append(
                ReviewRead(
                    id=review.id,
                    user_id=review.user_id,
                    user_email=user.email,
                    session_id=review.session_id,
                    rating=review.rating,
                    comment=review.comment,
                    date=review.created_at.date(),
                )
            )
        return review_list

    def _get_review_statistics(self) -> ReviewStatistics:
        stmt = sqlalchemy_select(
            func.avg(Review.rating),
            func.count(case((Review.rating == 5, 1))),  # type: ignore
            func.count(case((Review.rating == 4, 1))),  # type: ignore
            func.count(case((Review.rating == 3, 1))),  # type: ignore
            func.count(case((Review.rating == 2, 1))),  # type: ignore
            func.count(case((Review.rating == 1, 1))),  # type: ignore
        )

        avg, five, four, three, two, one = self.db.exec(stmt).one()  # type: ignore
        return ReviewStatistics(
            average=round(avg or 0, 2),
            num_five_star=five,
            num_four_star=four,
            num_three_star=three,
            num_two_star=two,
            num_one_star=one,
        )

    def _get_paginated_reviews(
        self,
        page: int | None = Query(None),
        page_size: int = Query(10),
        sort: str = Query('newest'),
    ) -> PaginatedReviewsResponse:
        """Retrieve paginated reviews with optional sorting."""

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

        joined_reviews_users = self._query_reviews_with_users(
            sort=sort, limit=page_size, offset=offset
        )
        review_list = self._build_review_read_list(joined_reviews_users)

        review_statistics = self._get_review_statistics()

        return PaginatedReviewsResponse(
            reviews=review_list,
            pagination={
                'currentPage': page if page else 1,
                'totalPages': total_pages,
                'totalCount': total_count,
                'pageSize': page_size,
            },
            rating_statistics=review_statistics,
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
            joined_reviews_users = self._query_reviews_with_users(sort=sort, limit=limit)
            return self._build_review_read_list(joined_reviews_users)

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
