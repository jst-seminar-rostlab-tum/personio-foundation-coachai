from datetime import datetime
from uuid import UUID

from app.models.camel_case import CamelModel


class LiveFeedbackCreate(CamelModel):
    # For testing and debugging
    session_turn_id: UUID
    session_id: UUID
    heading: str
    feedback_text: str


class LiveFeedbackRead(CamelModel):
    session_turn_id: UUID
    session_id: UUID
    heading: str
    feedback_text: str
    created_at: datetime
