from uuid import UUID

from app.models.camel_case import CamelModel


class LiveFeedbackLlmOutput(CamelModel):
    heading: str
    feedback_text: str


class LiveFeedbackRead(CamelModel):
    id: UUID
    heading: str
    feedback_text: str
