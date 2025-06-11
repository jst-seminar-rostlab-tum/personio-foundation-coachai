from datetime import UTC, datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import event
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Mapper
from sqlmodel import Field, Relationship

from app.models.camel_case import CamelModel

if TYPE_CHECKING:
    from app.models.confidence_area import ConfidenceArea
    from app.models.user_profile import UserProfile


class UserConfidenceScore(CamelModel, table=True):
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


class UserConfidenceScoreCreate(CamelModel):
    area_id: UUID
    user_id: UUID
    score: int


class UserConfidenceScoreRead(CamelModel):
    area_id: UUID
    user_id: UUID
    score: int
    updated_at: datetime


class ConfidenceScoreRead(CamelModel):
    area_label: str
    score: int
