"""Database model definitions for live feedback model."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlmodel import Field

from app.models.camel_case import CamelModel


class LiveFeedback(CamelModel, table=True):
    """Database model for live feedback."""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    session_id: UUID = Field(foreign_key='session.id', ondelete='CASCADE')
    heading: str
    feedback_text: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
