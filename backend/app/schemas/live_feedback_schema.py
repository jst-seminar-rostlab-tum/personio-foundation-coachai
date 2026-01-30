"""Pydantic schema definitions for live feedback schema."""

from uuid import UUID

from app.models.camel_case import CamelModel


class LiveFeedbackLlmOutput(CamelModel):
    """Schema for live feedback llm output."""

    heading: str
    feedback_text: str


class LiveFeedbackRead(CamelModel):
    """Schema for live feedback read."""

    id: UUID
    heading: str
    feedback_text: str
