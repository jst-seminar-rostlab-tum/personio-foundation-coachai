from datetime import UTC, datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import event
from sqlalchemy.engine import Connection
from sqlalchemy.orm.mapper import Mapper
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.training_session import TrainingSession
    from app.models.user_profile import UserProfile


class Rating(SQLModel, table=True):  # `table=True` makes it a database table
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    session_id: UUID = Field(foreign_key='trainingsession.id')  # FK to TrainingSession
    user_id: UUID = Field(foreign_key='userprofile.id', nullable=False)  # FK to UserProfile
    score: int
    comment: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    session: Optional['TrainingSession'] = Relationship(back_populates='ratings')
    user: Optional['UserProfile'] = Relationship(back_populates='ratings')


@event.listens_for(Rating, 'before_update')
def update_timestamp(mapper: Mapper, connection: Connection, target: 'Rating') -> None:
    target.updated_at = datetime.now(UTC)


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
