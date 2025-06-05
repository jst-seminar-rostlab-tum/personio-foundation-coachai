from datetime import UTC, datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import event
from sqlalchemy.engine.base import Connection
from sqlalchemy.orm.mapper import Mapper
from sqlmodel import Field, Relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.confidence_area import ConfidenceArea
    from app.models.user_profile import UserProfile


class UserConfidenceScore(BaseModel, table=True):
    area_id: UUID = Field(foreign_key='confidencearea.id', primary_key=True)
    user_id: UUID = Field(foreign_key='userprofile.id', primary_key=True)
    score: int
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    confidence_area: Optional['ConfidenceArea'] = Relationship(
        back_populates='user_confidence_scores'
    )
    user: Optional['UserProfile'] = Relationship(back_populates='user_confidence_scores')


# Automatically update `updated_at` before an update
@event.listens_for(UserConfidenceScore, 'before_update')
def update_timestamp(mapper: Mapper, connection: Connection, target: 'UserConfidenceScore') -> None:
    target.updated_at = datetime.now(UTC)


class UserConfidenceScoreCreate(BaseModel):
    area_id: UUID
    user_id: UUID
    score: int


class UserConfidenceScoreRead(BaseModel):
    area_id: UUID
    user_id: UUID
    score: int
    updated_at: datetime


class ConfidenceScoreRead(BaseModel):
    area_label: str
    score: int
