"""Service layer for review service."""

from collections.abc import Sequence
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import case, func
from sqlalchemy import select as sqlalchemy_select
from sqlmodel import Session as DBSession
from sqlmodel import asc, desc, select

from app.enums.account_role import AccountRole
from app.models.conversation_scenario import ConversationScenario
from app.models.review import Review
from app.models.session import Session
from app.models.user_profile import UserProfile
from app.schemas.review import (
    PaginatedReviewRead,
    ReviewConfirm,
    ReviewCreate,
    ReviewRead,
    ReviewStatistics,
)


class ReviewService:
    """Service for creating and querying user reviews."""

    def __init__(self, db: DBSession) -> None:
        """Initialize the service with a database session.

        Parameters:
            db (DBSession): Database session used for queries and mutations.
        """
        self.db = db

    def _query_reviews_with_users(
        self,
        sort: str = 'newest',
        limit: int | None = None,
        offset: int | None = None,
    ) -> Sequence[tuple[Review, UserProfile]]:
        """Query reviews joined with user profiles.

        Parameters:
            sort (str): Sorting strategy (newest, oldest, highest, lowest).
            limit (int | None): Max number of records to return.
            offset (int | None): Offset for pagination.

        Returns:
            Sequence[tuple[Review, UserProfile]]: Joined review and user rows.
        """
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
        """Build ReviewRead objects from joined rows.

        Parameters:
            joined_reviews_users (Sequence[tuple[Review, UserProfile]]): Joined rows.

        Returns:
            list[ReviewRead]: Review DTOs.
        """
        review_list = []
        for review, user in joined_reviews_users:
            session = None
            if review.session_id:
                session = self.db.get(Session, review.session_id)

            review_list.append(
                ReviewRead(
                    id=review.id,
                    user_id=review.user_id,
                    user_email=user.email,
                    session_id=review.session_id,
                    rating=review.rating,
                    comment=review.comment,
                    allow_admin_access=session.allow_admin_access if session else False,
                    date=review.created_at.date(),
                )
            )
        return review_list

    def _get_review_statistics(self) -> ReviewStatistics:
        """Compute aggregate review statistics.

        Returns:
            ReviewStatistics: Aggregated ratings data.
        """
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
        page: int | None = None,
        page_size: int = 10,
        sort: str = 'newest',
    ) -> PaginatedReviewRead:
        """Retrieve paginated reviews with optional sorting.

        Parameters:
            page (int | None): Page number (1-based).
            page_size (int): Number of items per page.
            sort (str): Sorting strategy (newest, oldest, highest, lowest).

        Returns:
            PaginatedReviewRead: Paginated reviews and statistics.
        """

        # Pagination
        total_count = self.db.exec(select(func.count()).select_from(Review)).one()
        if total_count == 0:
            return PaginatedReviewRead(
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

        return PaginatedReviewRead(
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
        page: int | None = None,
        page_size: int = 8,
        sort: str = 'newest',
    ) -> PaginatedReviewRead:
        """Retrieve user reviews with pagination, sorting and statistics.

        Parameters:
            page (int | None): Page number (1-based).
            page_size (int): Number of items per page.
            sort (str): Sorting strategy (newest, oldest, highest, lowest).

        Returns:
            PaginatedReviewRead: Paginated reviews and statistics.
        """
        return self._get_paginated_reviews(page, page_size, sort)

    def has_user_reviewed_session(self, session_id: UUID, user_id: UUID) -> bool:
        """Check if the current user has already submitted a review for this session.

        Parameters:
            session_id (UUID): Session identifier.
            user_id (UUID): User identifier.

        Returns:
            bool: True if a review exists.
        """
        review = self.db.exec(
            select(Review).where(Review.session_id == session_id, Review.user_id == user_id)
        ).first()
        return review is not None

    def _check_session_review_permissions(
        self,
        session_id: UUID,
        user_profile: UserProfile,
    ) -> None:
        """Check if the user has permission to create a review for the given session.

        Parameters:
            session_id (UUID): Session identifier.
            user_profile (UserProfile): Requesting user profile.

        Raises:
            HTTPException: If the session does not exist or the user does not have permission.
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
    ) -> ReviewConfirm:
        """Create a review and optionally grant admin session access.

        Parameters:
            review (ReviewCreate): Review payload.
            user_profile (UserProfile): Requesting user profile.

        Returns:
            ReviewConfirm: Confirmation message and review ID.

        Raises:
            HTTPException: If validation fails or permissions are missing.
        """
        user_id = user_profile.id  # Logged-in user's ID

        # Check if the user has already reviewed this session
        if review.session_id and self.has_user_reviewed_session(review.session_id, user_id):
            raise HTTPException(
                status_code=409,
                detail='User has already submitted a review for this session.',
            )

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

        # if allow_admin_access allows admin access to the session of the review
        if review.allow_admin_access and new_review.session_id:
            session = self.db.get(Session, new_review.session_id)
            if session:
                session.allow_admin_access = True
                self.db.add(session)
                self.db.commit()
                self.db.refresh(session)

        return ReviewConfirm(
            message='Review submitted successfully',
            review_id=new_review.id,
        )
