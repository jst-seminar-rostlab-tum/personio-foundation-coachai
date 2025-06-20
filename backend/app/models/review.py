from datetime import date, datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship

from app.models.camel_case import CamelModel

if TYPE_CHECKING:
    from app.models.session import Session
    from app.models.user_profile import UserProfile


class Review(CamelModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key='userprofile.id', ondelete='CASCADE')
    session_id: Optional[UUID] = Field(foreign_key='session.id', default=None, ondelete='CASCADE')
    rating: int = Field(ge=1, le=5)
    comment: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    # Relationships

    user_profile: 'UserProfile' = Relationship(back_populates='reviews')
    session: Optional['Session'] = Relationship(back_populates='session_review')


# Schema for creating a new review
class ReviewCreate(CamelModel):
    session_id: UUID | None = None  # Optional, can be None if not related to a session
    rating: int
    comment: str


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
