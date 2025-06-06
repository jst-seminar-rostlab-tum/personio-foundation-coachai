from datetime import date
from typing import Optional
from uuid import UUID

from sqlmodel import SQLModel


# Schema for returning a review item
# Information about a review item is retrieved from the user feedbacks and profiles
# This schema is used to return a list of reviews with pagination
class ReviewItem(SQLModel):
    id: UUID
    user_name: Optional[str]
    rating: int
    comment: str
    date: date


class PaginatedReviewsResponse(SQLModel):
    reviews: list[ReviewItem]
    pagination: dict
