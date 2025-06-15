from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import event
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Mapper
from sqlmodel import Field, Relationship

from app.models.camel_case import CamelModel

if TYPE_CHECKING:
    from app.models.user_profile import UserProfile


class ConfidenceArea(str, Enum):
    # Define the confidence areas as needed
    giving_difficult_feedback = 'giving_difficult_feedback'
    managing_team_conflicts = 'managing_team_conflicts'
    leading_challenging_conversations = 'leading_challenging_conversations'


class UserConfidenceScore(CamelModel, table=True):
    confidence_area: ConfidenceArea = Field(default=ConfidenceArea.giving_difficult_feedback,
                                            primary_key=True)
    user_id: UUID = Field(foreign_key='userprofile.id', primary_key=True)
    score: int
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    user: Optional['UserProfile'] = Relationship(back_populates='user_confidence_scores')


# Automatically update `updated_at` before an update
@event.listens_for(UserConfidenceScore, 'before_update')
def update_timestamp(mapper: Mapper, connection: Connection, target: 'UserConfidenceScore') -> None:
    target.updated_at = datetime.now(UTC)


class UserConfidenceScoreCreate(CamelModel):
    confidence_area: ConfidenceArea
    user_id: UUID
    score: int


class UserConfidenceScoreRead(CamelModel):
    confidence_area: ConfidenceArea
    user_id: UUID
    score: int
    updated_at: datetime


class ConfidenceScoreRead(CamelModel):
    confidence_area: ConfidenceArea
    score: int
