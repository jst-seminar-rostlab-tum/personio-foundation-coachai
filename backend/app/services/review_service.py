from collections.abc import Sequence
from uuid import UUID

from fastapi import HTTPException, Query
from sqlmodel import Session as DBSession
from sqlmodel import asc, desc, select

from app.models.review import Review
from app.models.user_profile import UserProfile
from app.schemas.review import (
    PaginatedReviewsResponse,
    ReviewRead,
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
        total_count = len(self.db.exec(select(Review)).all())
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
