"""Pydantic schema definitions for user confidence score."""

from app.enums.confidence_area import ConfidenceArea
from app.models.camel_case import CamelModel


class ConfidenceScoreRead(CamelModel):
    """Schema for confidence score read."""

    confidence_area: ConfidenceArea
    score: int
