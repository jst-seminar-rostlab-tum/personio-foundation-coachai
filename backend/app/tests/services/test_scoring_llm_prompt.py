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
        f'Structure: {scores.get("structure", "N/A")} | '
        f'Empathy: {scores.get("empathy", "N/A")} | '
        f'Focus: {scores.get("focus", "N/A")} | '
        f'Clarity: {scores.get("clarity", "N/A")}'
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
        print(f'Good Example -> {format_scores(result)}')

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

        scores_dict = {s.metric.lower(): s.score for s in result.scoring.scores}
        empathy_score = scores_dict.get('empathy')

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

        scores_dict = {s.metric.lower(): s.score for s in result.scoring.scores}
        clarity_score = scores_dict.get('clarity')
        structure_score = scores_dict.get('structure')

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

        scores_dict = {s.metric.lower(): s.score for s in result.scoring.scores}
        focus_score = scores_dict.get('focus')

        self.assertIsNotNone(focus_score, "Metric 'Focus' not found in response.")
        self.assertLessEqual(focus_score, 2)
        print(f'Low Focus    -> {format_scores(result)}')

    def test_score_conversation_structure_1(self) -> None:
        structure_1_path = self.base_path / 'dummy_conversation_structure_1.json'
        scoring_service = ScoringService(conversation_path=structure_1_path)
        with patch('app.connections.openai_client.ENABLE_AI', True):
            result = scoring_service.score_conversation()
        self.assertIsInstance(result, ScoringResult)
        scores_dict = {s.metric.lower(): s.score for s in result.scoring.scores}
        self.assertEqual(scores_dict.get('structure'), 1)
        print(f'Structure 1  -> {format_scores(result)}')

    def test_score_conversation_structure_2(self) -> None:
        structure_2_path = self.base_path / 'dummy_conversation_structure_2.json'
        scoring_service = ScoringService(conversation_path=structure_2_path)
        with patch('app.connections.openai_client.ENABLE_AI', True):
            result = scoring_service.score_conversation()
        self.assertIsInstance(result, ScoringResult)
        scores_dict = {s.metric.lower(): s.score for s in result.scoring.scores}
        self.assertEqual(scores_dict.get('structure'), 2)
        print(f'Structure 2  -> {format_scores(result)}')

    def test_score_conversation_structure_3(self) -> None:
        structure_3_path = self.base_path / 'dummy_conversation_structure_3.json'
        scoring_service = ScoringService(conversation_path=structure_3_path)
        with patch('app.connections.openai_client.ENABLE_AI', True):
            result = scoring_service.score_conversation()
        self.assertIsInstance(result, ScoringResult)
        scores_dict = {s.metric.lower(): s.score for s in result.scoring.scores}
        self.assertEqual(scores_dict.get('structure'), 3)
        print(f'Structure 3  -> {format_scores(result)}')

    def test_score_conversation_structure_4(self) -> None:
        structure_4_path = self.base_path / 'dummy_conversation_structure_4.json'
        scoring_service = ScoringService(conversation_path=structure_4_path)
        with patch('app.connections.openai_client.ENABLE_AI', True):
            result = scoring_service.score_conversation()
        self.assertIsInstance(result, ScoringResult)
        scores_dict = {s.metric.lower(): s.score for s in result.scoring.scores}
        self.assertEqual(scores_dict.get('structure'), 4)
        print(f'Structure 4  -> {format_scores(result)}')

    def test_score_conversation_structure_5(self) -> None:
        structure_5_path = self.base_path / 'dummy_conversation_structure_5.json'
        scoring_service = ScoringService(conversation_path=structure_5_path)
        with patch('app.connections.openai_client.ENABLE_AI', True):
            result = scoring_service.score_conversation()
        self.assertIsInstance(result, ScoringResult)
        scores_dict = {s.metric.lower(): s.score for s in result.scoring.scores}
        self.assertEqual(scores_dict.get('structure'), 5)
        print(f'Structure 5  -> {format_scores(result)}')

    def test_score_conversation_assistant_bad(self) -> None:
        """
        Test that a conversation with a high-quality User and extremely poor/nonsensical Assistant
        gives the User scores that are the same as (or very close to) the good example.
        """
        good_path = self.base_path / 'dummy_conversation_structure_5.json'
        assistant_bad_path = self.base_path / 'dummy_conversation_assistant_bad.json'
        scoring_service_good = ScoringService(conversation_path=good_path)
        scoring_service_bad = ScoringService(conversation_path=assistant_bad_path)

        with patch('app.connections.openai_client.ENABLE_AI', True):
            result_good = scoring_service_good.score_conversation()
            result_bad = scoring_service_bad.score_conversation()

        self.assertIsInstance(result_good, ScoringResult)
        self.assertIsInstance(result_bad, ScoringResult)

        scores_good = {s.metric.lower(): s.score for s in result_good.scoring.scores}
        scores_bad = {s.metric.lower(): s.score for s in result_bad.scoring.scores}

        for metric in ['structure', 'clarity', 'empathy', 'focus']:
            self.assertLessEqual(
                abs(scores_good.get(metric, 0) - scores_bad.get(metric, 0)),
                1,
                f'{metric} score differs by more than 1: good={scores_good.get(metric)}, '
                f'bad={scores_bad.get(metric)}',
            )

        print(f'Good Example   -> {format_scores(result_good)}')
        print(f'Assistant Bad  -> {format_scores(result_bad)}')

        self.assertGreaterEqual(scores_good.get('structure', 0), scores_bad.get('structure', 0))
        self.assertGreaterEqual(scores_good.get('clarity', 0), scores_bad.get('clarity', 0))
        self.assertGreaterEqual(scores_good.get('empathy', 0), scores_bad.get('empathy', 0))
        self.assertGreaterEqual(scores_good.get('focus', 0), scores_bad.get('focus', 0))


if __name__ == '__main__':
    unittest.main()
