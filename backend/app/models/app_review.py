from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class AppReview(SQLModel, table=True):  # `table=True` makes it a database table
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key='userprofile.id', nullable=False)  # FK to UserProfile
    rating: int
    comment: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Schema for creating a new user feedback
class AppReviewCreate(SQLModel):
    user_id: UUID
    rating: int
    comment: str


# Schema for reading user feedback data
class AppReviewRead(SQLModel):
    id: UUID
    user_id: UUID
    rating: int
    comment: str
    created_at: datetime


class AppReviewResponse(SQLModel):
    message: str = 'Feedback submitted successfully'
    feedback_id: UUID
