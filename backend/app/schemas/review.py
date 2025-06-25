from datetime import date
from uuid import UUID

from app.models.camel_case import CamelModel


# Schema for creating a new review
class ReviewCreate(CamelModel):
    session_id: UUID | None = None  # Optional, can be None if not related to a session
    rating: int
    comment: str
    allow_admin_access: bool = False  # admin access to session details


class ReviewResponse(CamelModel):
    message: str = 'Review submitted successfully'
    review_id: UUID


# Schema for reading review data
class ReviewRead(CamelModel):
    id: UUID
    user_id: UUID
    user_email: str
    session_id: UUID | None = None  # Optional, can be None if not related to a session
    rating: int
    comment: str
    allow_admin_access: bool = False  # admin access to session details
    date: date


class ReviewStatistics(CamelModel):
    average: float
    num_five_star: int
    num_four_star: int
    num_three_star: int
    num_two_star: int
    num_one_star: int


class PaginatedReviewsResponse(CamelModel):
    reviews: list[ReviewRead]
    pagination: dict
    rating_statistics: ReviewStatistics
