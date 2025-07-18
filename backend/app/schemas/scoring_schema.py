from pydantic import Field, conint

from app.models.camel_case import CamelModel


class MetricScore(CamelModel):
    metric: str = Field(
        ..., description="The name of the metric being scored, e.g., 'Structure', 'Empathy'."
    )
    score: conint(ge=1, le=5) = Field(..., description='The score for the metric, from 1 to 5.')
    justification: str = Field(
        ..., description='The justification from the LLM for why this score was given.'
    )


class ConversationScore(CamelModel):
    overall_score: float = Field(..., description='The sum of all scores across all metrics.')
    scores: list[MetricScore] = Field(
        ..., description='A list of scores for each individual metric.'
    )


class ScoringRead(CamelModel):
    conversation_summary: str = Field(..., description='A brief summary of the conversation.')
    scoring: ConversationScore = Field(..., description='The detailed scoring of the conversation.')
