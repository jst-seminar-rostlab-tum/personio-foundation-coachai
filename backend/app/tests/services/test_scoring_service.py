import json
import unittest
from pathlib import Path

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
                    'scenario': {'description': 'Test scenario'},
                    'transcript': [{'speaker': 'A', 'message': 'Hello'}],
                },
                f,
            )

        self.scoring_service = ScoringService(
            rubric_path=self.rubric_path, conversation_path=self.conversation_path
        )

    def tearDown(self) -> None:
        """Remove temporary files after tests are done."""
        self.rubric_path.unlink()
        self.conversation_path.unlink()
        self.test_data_dir.rmdir()

    def test_initialization(self) -> None:
        """Test if the service initializes correctly and loads the data."""
        self.assertIsNotNone(self.scoring_service.rubric)
        self.assertIsNotNone(self.scoring_service.conversation_data)
        self.assertEqual(self.scoring_service.rubric['title'], 'Test Rubric')

    def test_score_conversation_returns_valid_structure(self) -> None:
        """Test if the mocked score_conversation method returns the correct Pydantic model."""
        result = self.scoring_service.score_conversation()

        # Check if the result is of the correct type
        self.assertIsInstance(result, ScoringResult)

        # Check some of the contents of the mocked response
        self.assertIsInstance(result.conversation_summary, str)
        self.assertGreater(len(result.conversation_summary), 0)
        self.assertEqual(result.scoring.overall_score, 4.25)
        self.assertEqual(len(result.scoring.scores), 4)

        first_metric = result.scoring.scores[0]
        self.assertEqual(first_metric.metric, 'Structure')
        self.assertEqual(first_metric.score, 5)

    def test_build_prompt(self) -> None:
        """Test if the prompt is built correctly."""
        prompt = self.scoring_service._build_prompt()
        self.assertIn('Test Rubric', prompt)
        self.assertIn('Test scenario', prompt)
        self.assertIn('A: Hello', prompt)
        self.assertIn('Provide a score from 0-5', prompt)


if __name__ == '__main__':
    unittest.main()
