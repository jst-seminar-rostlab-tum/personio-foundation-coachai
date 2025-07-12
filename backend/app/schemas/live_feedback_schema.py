from uuid import UUID

from app.models.camel_case import CamelModel


class LiveFeedback(CamelModel):
    id: UUID
    heading: str
    feedback_text: str
