from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlmodel import Field

from app.models.camel_case import CamelModel


class LiveFeedback(CamelModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    session_id: UUID = Field(foreign_key='session.id', primary_key=False)
    heading: str
    feedback_text: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
