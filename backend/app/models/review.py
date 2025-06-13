from datetime import date, datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Review(SQLModel, table=True):  # `table=True` makes it a database table
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key='userprofile.id', nullable=False)  # FK to UserProfile
    session_id: UUID | None = Field(
        foreign_key='session.id', nullable=True, default=None
    )  # FK to Session
    rating: int = Field(ge=1, le=5)
    comment: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Schema for creating a new review
class ReviewCreate(SQLModel):
    user_id: UUID
    session_id: UUID | None = None  # Optional, can be None if not related to a session
    rating: int
    comment: str


class ReviewResponse(SQLModel):
    message: str = 'Review submitted successfully'
    review_id: UUID


# Schema for reading review data
class ReviewRead(SQLModel):
    id: UUID
    user_id: UUID
    session_id: UUID | None = None  # Optional, can be None if not related to a session
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
    reviews: list[ReviewRead]
    pagination: dict
    rating_statistics: ReviewStatistics
