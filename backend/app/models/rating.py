from datetime import UTC, datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import event
from sqlalchemy.engine.base import Connection
from sqlalchemy.orm.mapper import Mapper
from sqlmodel import Field, Relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.training_session import TrainingSession
    from app.models.user_profile import UserProfile


class Rating(BaseModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    session_id: UUID = Field(
        foreign_key='trainingsession.id', alias='sessionId'
    )  # FK to TrainingSession
    user_id: UUID = Field(foreign_key='userprofile.id', nullable=False)  # FK to UserProfile
    score: int
    comment: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    session: Optional['TrainingSession'] = Relationship(back_populates='ratings')
    user_profile: Optional['UserProfile'] = Relationship(back_populates='ratings')


# Automatically update `updated_at` before an update
@event.listens_for(Rating, 'before_update')
def update_timestamp(mapper: Mapper, connection: Connection, target: 'Rating') -> None:
    target.updated_at = datetime.now(UTC)


# Schema for creating a new Rating
class RatingCreate(BaseModel):
    session_id: UUID
    user_id: UUID
    score: int
    comment: str


# Schema for reading Rating data
class RatingRead(BaseModel):
    id: UUID
    session_id: UUID
    user_id: UUID
    score: int
    comment: str
    created_at: datetime
    updated_at: datetime
