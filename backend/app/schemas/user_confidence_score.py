from app.models.camel_case import CamelModel
from app.models.user_confidence_score import ConfidenceArea


class ConfidenceScoreRead(CamelModel):
    confidence_area: ConfidenceArea
    score: int
