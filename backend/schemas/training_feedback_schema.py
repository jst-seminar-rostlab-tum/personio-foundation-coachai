from pydantic import BaseModel, Field


class TrainingFeedbackBase(BaseModel):
    transcript: str  # Full transcript of the training session
    objectives: list[str] = Field(
        ..., description='List of training objectives the user is expected to achieve'
    )


class ExamplesRequest(TrainingFeedbackBase):
    category: str = Field(..., description='Training category')
    goal: str = Field(..., description='Training goal')
    context: str = Field(..., description='Training context')
    other_party: str = Field(..., description='Persona spoken with')
    key_concepts: str  # Can be markdown or plain text


class PositiveExample(BaseModel):
    heading: str = Field(..., description='Title or summary of the positive example')
    text: str = Field(..., description='Explanation of why this is a good example')
    quote: str = Field(..., description='Direct quote from the transcript')
    guideline: str = Field(..., description='Specific guideline or concept this quote aligns with')


class NegativeExample(BaseModel):
    heading: str = Field(..., description='Title or summary of the negative example')
    text: str = Field(..., description='Description or context of the example')
    quote: str = Field(..., description='Problematic or unhelpful quote mentioned by the user')
    improved_quote: str = Field(..., description='Suggested improved version of the quote')


class TrainingExamplesCollection(BaseModel):
    positive_examples: list[PositiveExample] = Field(..., description='List of positive examples')
    negative_examples: list[NegativeExample] = Field(..., description='List of negative examples')


class GoalAchievementRequest(TrainingFeedbackBase):
    """Request to evaluate how many training goals (objectives) were achieved in the transcript."""

    pass
