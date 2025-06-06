from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class UserFeedback(SQLModel, table=True):  # `table=True` makes it a database table
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key='userprofile.id', nullable=False)  # FK to UserProfile
    rating: int
    comment: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Schema for creating a new user feedback
class UserFeedbackCreate(SQLModel):
    user_id: UUID
    rating: int
    comment: str


# Schema for reading user feedback data
class UserFeedbackRead(SQLModel):
    id: UUID
    user_id: UUID
    rating: int
    comment: str
    created_at: datetime


class UserFeedbackResponse(SQLModel):
    message: str = 'Feedback submitted successfully'
    feedback_id: UUID
