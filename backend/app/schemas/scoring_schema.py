from pydantic import BaseModel, Field


class MetricScore(BaseModel):
    metric: str = Field(
        ..., description="The name of the metric being scored, e.g., 'Structure', 'Empathy'."
    )
    score: int = Field(..., ge=0, le=5, description='The score for the metric, from 0 to 5.')
    justification: str = Field(
        ..., description='The justification from the LLM for why this score was given.'
    )


class ConversationScore(BaseModel):
    overall_score: float = Field(..., description='The average score across all metrics.')
    scores: list[MetricScore] = Field(
        ..., description='A list of scores for each individual metric.'
    )


class ScoringRequest(BaseModel):
    scenario: dict
    transcript: list[dict]


class ScoringResult(BaseModel):
    conversation_summary: str = Field(..., description='A brief summary of the conversation.')
    scoring: ConversationScore = Field(..., description='The detailed scoring of the conversation.')
