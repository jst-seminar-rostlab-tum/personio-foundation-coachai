from datetime import UTC, datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import event
from sqlalchemy.engine.base import Connection
from sqlalchemy.orm.mapper import Mapper
from sqlmodel import Field, Relationship

from app.enums.session_status import SessionStatus
from app.models.camel_case import CamelModel

if TYPE_CHECKING:
    from app.models.conversation_scenario import ConversationScenario
    from app.models.review import Review
    from app.models.session_feedback import SessionFeedback
    from app.models.session_turn import SessionTurn


class Session(CamelModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    scenario_id: UUID = Field(foreign_key='conversationscenario.id', ondelete='CASCADE')
    scheduled_at: datetime | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None
    status: SessionStatus = Field(default=SessionStatus.started)
    allow_admin_access: bool = Field(
        default=False, description='If True, admin can view this session details'
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    scenario: 'ConversationScenario' = Relationship(back_populates='sessions')
    session_turns: list['SessionTurn'] = Relationship(back_populates='session', cascade_delete=True)
    feedback: Optional['SessionFeedback'] = Relationship(
        back_populates='session', cascade_delete=True
    )
    session_review: Optional['Review'] = Relationship(back_populates='session', cascade_delete=True)


@event.listens_for(Session, 'before_update')
def update_timestamp(mapper: Mapper, connection: Connection, target: 'Session') -> None:
    target.updated_at = datetime.now(UTC)
