from pydantic import Field

from app.models.camel_case import CamelModel


class ExamplesRequest(CamelModel):
    transcript: str | None  # Full transcript of the session
    objectives: list[str] = Field(
        ..., description='List of training objectives the user is expected to achieve'
    )
    category: str = Field(..., description='Training category')
    goal: str = Field(..., description='Training goal')
    context: str = Field(..., description='Training context')
    other_party: str = Field(..., description='Persona spoken with')
    key_concepts: str  # Can be markdown or plain text


class PositiveExample(CamelModel):
    heading: str = Field(..., description='Title or summary of the positive example')
    quote: str = Field(..., description='Direct quote from the transcript')
    text: str = Field(..., description='Explanation of why this is a good example')
    guideline: str = Field(..., description='Guidelines for the user to follow')


class NegativeExample(CamelModel):
    heading: str = Field(..., description='Title or summary of the negative example')
    quote: str = Field(..., description='Problematic or unhelpful quote mentioned by the user')
    text: str = Field(..., description='Explanation of why this is a bad example')
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


class GoalsAchievedCollection(CamelModel):
    """Response indicating the training goals that were achieved."""

    goals_achieved: list[str] = Field(
        ..., description='List of training objectives achieved in the session'
    )


class RecommendationsRequest(ExamplesRequest):
    """Request to generate improvement recommendations based on session feedback.
    Same fields as ExamplesRequest, but used for generating recommendations instead of examples.
    """

    pass


class Recommendation(CamelModel):
    heading: str = Field(..., description='Title or summary of the recommendation')
    text: str = Field(..., description='Description or elaboration of the recommendation')


class RecommendationsCollection(CamelModel):
    recommendations: list[Recommendation] = Field(
        ..., description='List of improvement recommendations'
    )
