import os
import unittest
from pathlib import Path
from unittest.mock import patch

from app.schemas.scoring_schema import ScoringResult
from app.services.scoring_service import ScoringService


def format_scores(result: ScoringResult) -> str:
    """Helper function to format all metric scores for printing."""
    scores = {s.metric: s.score for s in result.scoring.scores}
    return (
        f'Overall: {result.scoring.overall_score:.2f} | '
        f'Structure: {scores.get("Structure", "N/A")} | '
        f'Empathy: {scores.get("Empathy", "N/A")} | '
        f'Focus: {scores.get("Focus", "N/A")} | '
        f'Clarity: {scores.get("Clarity", "N/A")}'
    )


@unittest.skipIf(
    os.getenv('RUN_INTEGRATION_TESTS', 'false').lower() != 'true',
    'Skipping integration tests by default. Set RUN_INTEGRATION_TESTS=true to run.',
)
class TestScoringServiceIntegration(unittest.TestCase):
    def setUp(self) -> None:
        """Set up the scoring service for an integration test."""
        self.base_path = Path(__file__).parent.parent.parent / 'data'

    def test_score_conversation_integration_good_example(self) -> None:
        """
        Test the full end-to-end scoring process with a good conversation example.
        """
        good_conversation_path = self.base_path / 'dummy_conversation_good_example.json'
        scoring_service = ScoringService(conversation_path=good_conversation_path)

        with patch('app.connections.openai_client.ENABLE_AI', True):
            result = scoring_service.score_conversation()

        self.assertIsInstance(result, ScoringResult)
        self.assertGreaterEqual(result.scoring.overall_score, 3.5)
        print(f'\nGood Example -> {format_scores(result)}')

    def test_score_conversation_integration_low_empathy(self) -> None:
        """
        Test the full end-to-end scoring process with a low empathy conversation.
        """
        low_empathy_path = self.base_path / 'dummy_conversation_low_empathy.json'
        scoring_service = ScoringService(conversation_path=low_empathy_path)

        with patch('app.connections.openai_client.ENABLE_AI', True):
            result = scoring_service.score_conversation()

        self.assertIsInstance(result, ScoringResult)
        self.assertLess(result.scoring.overall_score, 3.0)

        scores_dict = {s.metric: s.score for s in result.scoring.scores}
        empathy_score = scores_dict.get('Empathy')

        self.assertIsNotNone(empathy_score, "Metric 'Empathy' not found in response.")
        self.assertLessEqual(empathy_score, 2)
        print(f'Low Empathy  -> {format_scores(result)}')

    def test_score_conversation_integration_low_clarity_structure(self) -> None:
        """
        Test the full end-to-end scoring process with a low clarity and structure conversation.
        """
        low_clarity_path = self.base_path / 'dummy_conversation_low_clarity_structure.json'
        scoring_service = ScoringService(conversation_path=low_clarity_path)

        with patch('app.connections.openai_client.ENABLE_AI', True):
            result = scoring_service.score_conversation()

        self.assertIsInstance(result, ScoringResult)
        self.assertLess(result.scoring.overall_score, 3.0)

        scores_dict = {s.metric: s.score for s in result.scoring.scores}
        clarity_score = scores_dict.get('Clarity')
        structure_score = scores_dict.get('Structure')

        self.assertIsNotNone(clarity_score, "Metric 'Clarity' not found in response.")
        self.assertIsNotNone(structure_score, "Metric 'Structure' not found in response.")
        self.assertLessEqual(clarity_score, 2)
        self.assertLessEqual(structure_score, 2)
        print(f'Low Clarity  -> {format_scores(result)}')

    def test_score_conversation_integration_low_focus(self) -> None:
        """
        Test the full end-to-end scoring process with a low focus conversation.
        """
        low_focus_path = self.base_path / 'dummy_conversation_low_focus.json'
        scoring_service = ScoringService(conversation_path=low_focus_path)

        with patch('app.connections.openai_client.ENABLE_AI', True):
            result = scoring_service.score_conversation()

        self.assertIsInstance(result, ScoringResult)
        self.assertLess(result.scoring.overall_score, 3.0)

        scores_dict = {s.metric: s.score for s in result.scoring.scores}
        focus_score = scores_dict.get('Focus')

        self.assertIsNotNone(focus_score, "Metric 'Focus' not found in response.")
        self.assertLessEqual(focus_score, 2)
        print(f'Low Focus    -> {format_scores(result)}')


if __name__ == '__main__':
    unittest.main()
