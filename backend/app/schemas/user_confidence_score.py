from app.enums.confidence_area import ConfidenceArea
from app.models.camel_case import CamelModel


class ConfidenceScoreRead(CamelModel):
    confidence_area: ConfidenceArea
    score: int
