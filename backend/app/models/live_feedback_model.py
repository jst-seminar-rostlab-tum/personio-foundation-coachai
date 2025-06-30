from datetime import UTC, datetime
from uuid import UUID

from sqlmodel import Field

from app.models.camel_case import CamelModel


class LiveFeedback(CamelModel, table=True):
    session_turn_id: UUID = Field(foreign_key='sessionturn.id', primary_key=True)
    heading: str
    feedback_text: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
