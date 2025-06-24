import json
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from app.schemas.scoring_schema import ScoringResult
from app.services.scoring_service import ScoringService


class TestScoringService(unittest.TestCase):
    def setUp(self) -> None:
        """Set up a temporary rubric and conversation file for testing."""
        self.test_data_dir = Path(__file__).parent / 'test_data'
        self.test_data_dir.mkdir(exist_ok=True)

        self.rubric_path = self.test_data_dir / 'test_rubric.json'
        self.conversation_path = self.test_data_dir / 'test_conversation.json'

        # Create dummy rubric file
        with open(self.rubric_path, 'w') as f:
            json.dump({'title': 'Test Rubric'}, f)

        # Create dummy conversation file
        with open(self.conversation_path, 'w') as f:
            json.dump(
                {
                    'scenario': {
                        'description': 'Test scenario',
                        'participants': {
                            'user_role': 'Manager',
                            'assistant_role': 'Direct Report',
                        },
                    },
                    'transcript': [{'speaker': 'User', 'message': 'Hello'}],
                },
                f,
            )

        self.scoring_service = ScoringService(
            rubric_path=self.rubric_path, conversation_path=self.conversation_path
        )

    def tearDown(self) -> None:
        """Remove temporary files after tests are done."""
        if self.rubric_path.exists():
            self.rubric_path.unlink()
        if self.conversation_path.exists():
            self.conversation_path.unlink()
        if self.test_data_dir.exists():
            self.test_data_dir.rmdir()

    def test_initialization(self) -> None:
        """Test if the service initializes correctly and loads the data."""
        self.assertIsNotNone(self.scoring_service.rubric)
        self.assertIsNotNone(self.scoring_service.conversation_data)
        self.assertEqual(self.scoring_service.rubric['title'], 'Test Rubric')

    @patch('app.services.scoring_service.call_structured_llm')
    def test_score_conversation_calls_llm_and_returns_valid_structure(
        self, mock_call_structured_llm: MagicMock
    ) -> None:
        """Test that score_conversation calls the LLM and returns its valid result."""
        # Arrange: Define the mock return value for the call_structured_llm function
        mock_result = ScoringResult(
            conversation_summary=(
                'The User initiated the conversation clearly and maintained a professional '
                'tone throughout the interaction.'
            ),
            scoring={
                'overall_score': 4.25,
                'scores': [
                    {'metric': 'Structure', 'score': 5, 'justification': 'Perfect.'},
                    {'metric': 'Empathy', 'score': 4, 'justification': 'Good.'},
                    {'metric': 'Focus', 'score': 4, 'justification': 'Good.'},
                    {'metric': 'Clarity', 'score': 4, 'justification': 'Good.'},
                ],
            },
        )
        mock_call_structured_llm.return_value = mock_result

        # Act: Call the method under test
        result = self.scoring_service.score_conversation()

        # Assert: Check that our mock LLM function was called exactly once
        mock_call_structured_llm.assert_called_once()

        # Assert: Check the arguments passed to the mock call
        _, kwargs = mock_call_structured_llm.call_args
        self.assertIn('request_prompt', kwargs)
        self.assertEqual(kwargs['output_model'], ScoringResult)

        # Assert: Check that the final result is the one returned by our mock
        self.assertEqual(result, mock_result)
        self.assertEqual(result.scoring.overall_score, 4.25)
        self.assertEqual(len(result.scoring.scores), 4)

    def test_build_prompt(self) -> None:
        """Test if the prompts are built correctly."""
        system_prompt = self.scoring_service._build_system_prompt()
        user_prompt = self.scoring_service._build_user_prompt()
        self.assertIn('Test Rubric', system_prompt)
        self.assertIn('Test scenario', user_prompt)
        self.assertIn('User: Hello', user_prompt)
        self.assertIn('provide a score from 1 to 5 for each metric', user_prompt)


if __name__ == '__main__':
    unittest.main()
