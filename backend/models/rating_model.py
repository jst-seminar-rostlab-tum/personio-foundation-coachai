from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from backend.models.training_session_model import TrainingSessionModel


class RatingModel(SQLModel, table=True):  # `table=True` makes it a database table
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    session_id: UUID = Field(foreign_key='trainingsessionmodel.id')  # FK to TrainingSessionModel
    user_id: UUID
    score: int
    comment: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    session: Optional['TrainingSessionModel'] = Relationship(back_populates='ratings')


# Schema for creating a new Rating
class RatingCreate(SQLModel):
    session_id: UUID
    user_id: UUID
    score: int
    comment: str


# Schema for reading Rating data
class RatingRead(SQLModel):
    id: UUID
    session_id: UUID
    user_id: UUID
    score: int
    comment: str
    created_at: datetime
    updated_at: datetime
