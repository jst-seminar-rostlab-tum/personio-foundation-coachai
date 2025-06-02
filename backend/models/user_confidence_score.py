from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import event
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Mapper
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from backend.models.confidence_area import ConfidenceArea
    from backend.models.user_profile import UserProfile


class UserConfidenceScore(SQLModel, table=True):
    area_id: UUID = Field(foreign_key='confidencearea.id', primary_key=True)
    user_id: UUID = Field(foreign_key='userprofile.id', primary_key=True)
    score: int
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    confidence_area: Optional['ConfidenceArea'] = Relationship(
        back_populates='user_confidence_scores'
    )
    user: Optional['UserProfile'] = Relationship(back_populates='user_confidence_scores')


@event.listens_for(UserConfidenceScore, 'before_update')
def update_timestamp(mapper: Mapper, connection: Connection, target: 'UserConfidenceScore') -> None:
    target.updated_at = datetime.now(datetime.timezone.utc)


class UserConfidenceScoreCreate(SQLModel):
    area_id: UUID
    user_id: UUID
    score: int


class UserConfidenceScoreRead(SQLModel):
    area_id: UUID
    user_id: UUID
    score: int
    updated_at: datetime


class ConfidenceScoreRead(SQLModel):
    area_label: str
    score: int
