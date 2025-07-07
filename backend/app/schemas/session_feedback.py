from sqlmodel import JSON, Column, Field

from app.models.camel_case import CamelModel
from app.models.language import LanguageCode


class FeedbackCreate(CamelModel):
    transcript: str | None  # Full transcript of the session
    objectives: list[str] = Field(
        ..., description='List of training objectives the user is expected to achieve'
    )
    category: str = Field(..., description='Training category')
    persona: str = Field(..., description='Persona or role the chatbot adopts during the session')
    situational_facts: str = Field(
        ..., description='Facts or context relevant to the training scenario'
    )
    key_concepts: str  # Can be markdown or plain text
    language_code: LanguageCode = Field(
        default=LanguageCode.en, description='Language code for the examples'
    )


class PositiveExample(CamelModel):
    heading: str = Field(..., description='Title or summary of the positive example')
    feedback: str = Field(..., description='Explanation of why this is a good example')
    quote: str = Field(..., description='Direct quote from the transcript')


class NegativeExample(CamelModel):
    heading: str = Field(..., description='Title or summary of the negative example')
    feedback: str = Field(..., description='Description or context of the example')
    quote: str = Field(..., description='Problematic or unhelpful quote mentioned by the user')
    improved_quote: str = Field(..., description='Suggested improved version of the quote')


class SessionExamplesCollection(CamelModel):
    positive_examples: list[PositiveExample] = Field(..., description='List of positive examples')
    negative_examples: list[NegativeExample] = Field(..., description='List of negative examples')


class GoalsAchievementRequest(CamelModel):
    """Request to evaluate the training objectives that were achieved in the transcript."""

    transcript: str | None
    objectives: list[str] = Field(
        ..., description='List of training objectives the user is expected to achieve'
    )
    language_code: LanguageCode = Field(
        default=LanguageCode.en, description='Language code for the goals achievement request'
    )


class GoalsAchievedCollection(CamelModel):
    """Response indicating the training goals that were achieved."""

    goals_achieved: list[str] = Field(
        ..., description='List of training objectives achieved in the session'
    )


class Recommendation(CamelModel):
    heading: str = Field(..., description='Title or summary of the recommendation')
    recommendation: str = Field(..., description='Description or elaboration of the recommendation')


class RecommendationsCollection(CamelModel):
    recommendations: list[Recommendation] = Field(
        ..., description='List of improvement recommendations'
    )


# Schema for reading a session's feedback metrics
class SessionFeedbackMetrics(CamelModel):
    scores: dict = Field(default_factory=dict, sa_column=Column(JSON))
    tone_analysis: dict = Field(default_factory=dict, sa_column=Column(JSON))
    overall_score: float
    transcript_uri: str
    speak_time_percent: float
    questions_asked: int
    session_length_s: int
    goals_achieved: list[str] = Field(default_factory=list)
    example_positive: list[PositiveExample] = Field(default_factory=list)
    example_negative: list[NegativeExample] = Field(default_factory=list)
    recommendations: list[Recommendation] = Field(default_factory=list)
