from datetime import UTC, datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import event
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Mapper
from sqlmodel import Field, Relationship

from app.enums.confidence_area import ConfidenceArea
from app.models.camel_case import CamelModel

if TYPE_CHECKING:
    from app.models.user_profile import UserProfile


class UserConfidenceScore(CamelModel, table=True):
    confidence_area: ConfidenceArea = Field(
        default=ConfidenceArea.giving_difficult_feedback, primary_key=True
    )
    user_id: UUID = Field(foreign_key='userprofile.id', primary_key=True, ondelete='CASCADE')
    score: int
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    user: Optional['UserProfile'] = Relationship(back_populates='user_confidence_scores')


@event.listens_for(UserConfidenceScore, 'before_update')
def update_timestamp(mapper: Mapper, connection: Connection, target: 'UserConfidenceScore') -> None:
    target.updated_at = datetime.now(UTC)
