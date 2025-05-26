from unittest.mock import MagicMock, patch

from backend.schemas.training_feedback_schema import (
    TrainingExamplesCollection,
    TrainingFeedbackRequest,
)
from backend.services.training_feedback_service import generate_training_examples


@patch('backend.services.training_feedback_service.client')
def test_generate_training_examples(mock_client: MagicMock) -> None:
    mock_response = MagicMock()
    mock_response.choices[0].message.content.strip.return_value = """
    {
      "positive_examples": [
        {
          "heading": "Clear Objective Addressed",
          "text": "The user successfully summarized the objective.",
          "quote": "I want to make sure we both feel heard and find a solution together.",
          "guideline": "Collaborative Problem-Solving"
        }
      ],
      "negative_examples": [
        {
          "heading": "Missed Empathy",
          "text": "The user dismissed the other party's concern.",
          "quote": "That's not important right now.",
          "improved_quote": "I understand your concern—let's come back to it in a moment."
        }
      ]
    }
    """
    mock_client.chat.completions.create.return_value = mock_response

    request = TrainingFeedbackRequest(
        category='Feedback',
        goal='Deliver constructive feedback',
        context='Performance review',
        other_party='Team member',
        transcript='User: I want to make sure we both feel heard..., '
        + 'AI: ..., '
        + "User: That's not important right now...",
        objectives=['Foster mutual understanding', 'Encourage open dialogue'],
        key_concepts='### Active Listening\nShow empathy and paraphrase concerns.',
    )

    result = generate_training_examples(request)
    assert isinstance(result, TrainingExamplesCollection)
    assert len(result.positive_examples) == 1
    assert len(result.negative_examples) == 1
    assert result.positive_examples[0].heading == 'Clear Objective Addressed'
    assert result.negative_examples[0].quote == "That's not important right now."
