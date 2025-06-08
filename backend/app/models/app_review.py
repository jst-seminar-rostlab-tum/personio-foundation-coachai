from datetime import date, datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class AppReview(SQLModel, table=True):  # `table=True` makes it a database table
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key='userprofile.id', nullable=False)  # FK to UserProfile
    rating: int = Field(ge=1, le=5)
    comment: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Schema for creating a new app review
class AppReviewCreate(SQLModel):
    user_id: UUID
    rating: int
    comment: str


class AppReviewResponse(SQLModel):
    message: str = 'Feedback submitted successfully'
    app_review_id: UUID


# Schema for reading app review data
class AppReviewRead(SQLModel):
    id: UUID
    user_id: UUID
    rating: int
    comment: str
    date: date


class ReviewStatistics(SQLModel):
    average: float
    num_five_star: int
    num_four_star: int
    num_three_star: int
    num_two_star: int
    num_one_star: int


class PaginatedReviewsResponse(SQLModel):
    reviews: list[AppReviewRead]
    pagination: dict
    rating_statistics: ReviewStatistics
