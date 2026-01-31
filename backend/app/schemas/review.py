"""Pydantic schema definitions for review."""

from datetime import date
from uuid import UUID

from app.models.camel_case import CamelModel


# Schema for creating a new review
class ReviewCreate(CamelModel):
    """Schema for review create."""

    session_id: UUID | None = None  # Optional, can be None if not related to a session
    rating: int
    comment: str
    allow_admin_access: bool = False  # admin access to session details


class ReviewConfirm(CamelModel):
    """Schema for review confirm."""

    message: str = 'Review submitted successfully'
    review_id: UUID


# Schema for reading review data
class ReviewRead(CamelModel):
    """Schema for review read."""

    id: UUID
    user_id: UUID
    user_email: str
    session_id: UUID | None = None  # Optional, can be None if not related to a session
    rating: int
    comment: str
    allow_admin_access: bool = False  # admin access to session details
    date: date


class ReviewStatistics(CamelModel):
    """Schema for review statistics."""

    average: float
    num_five_star: int
    num_four_star: int
    num_three_star: int
    num_two_star: int
    num_one_star: int


class PaginatedReviewRead(CamelModel):
    """Schema for paginated review read."""

    reviews: list[ReviewRead]
    pagination: dict
    rating_statistics: ReviewStatistics
