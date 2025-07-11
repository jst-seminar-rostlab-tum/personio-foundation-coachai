# ruff: noqa: E501
import json
import os
import unittest
from pathlib import Path
from unittest.mock import patch

from app.schemas.conversation_scenario import (
    ConversationScenario,
    ConversationScenarioWithTranscript,
)
from app.schemas.scoring_schema import ScoringResult
from app.schemas.session_turn import SessionTurnRead
from app.services.scoring_service import ScoringService


def format_scores(result: ScoringResult) -> str:
    """Helper function to format all metric scores for printing."""
    scores = {s.metric: s.score for s in result.scoring.scores}
    return (
        f'Overall: {result.scoring.overall_score:.2f} | '
        f'Structure: {scores["structure"]} | '
        f'Empathy: {scores["empathy"]} | '
        f'Focus: {scores["focus"]} | '
        f'Clarity: {scores["clarity"]}'
    )


def load_conversation_data(json_path: Path) -> ConversationScenarioWithTranscript:
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)
    # scenario
    scenario = ConversationScenario(**data['scenario'])
    # transcript
    transcript = [SessionTurnRead(**turn) for turn in data['transcript']]
    return ConversationScenarioWithTranscript(scenario=scenario, transcript=transcript)


@unittest.skipUnless(os.environ.get('RUN_AI_TESTS') == 'true', 'AI test not enabled')
class TestScoringServiceIntegration(unittest.TestCase):
    def setUp(self) -> None:
        """Set up the scoring service for an integration test."""
        self.base_path = Path(__file__).parent.parent.parent / 'data'
        self.rubric_path = self.base_path / 'conversation_rubric.json'
        self.scoring_service = ScoringService(rubric_path=self.rubric_path)

    def test_score_conversation_integration_good_example(self) -> None:
        """
        Test the full end-to-end scoring process with a good conversation example.
        """
        good_conversation_path = self.base_path / 'dummy_conversation_good_example.json'
        conversation = load_conversation_data(good_conversation_path)
        with patch('app.connections.openai_client.ENABLE_AI', True):
            result = self.scoring_service.safe_score_conversation(conversation)

        self.assertIsInstance(result, ScoringResult)
        self.assertGreaterEqual(result.scoring.overall_score, 3.5)
        print(f'Good Example -> {format_scores(result)}')

    def test_score_conversation_integration_low_empathy(self) -> None:
        """
        Test the full end-to-end scoring process with a low empathy conversation.
        """
        low_empathy_path = self.base_path / 'dummy_conversation_low_empathy.json'
        conversation = load_conversation_data(low_empathy_path)
        with patch('app.connections.openai_client.ENABLE_AI', True):
            result = self.scoring_service.safe_score_conversation(conversation)

        self.assertIsInstance(result, ScoringResult)

        scores_dict = {s.metric.lower(): s.score for s in result.scoring.scores}
        empathy_score = scores_dict['empathy']

        self.assertIsNotNone(empathy_score, "Metric 'Empathy' not found in response.")
        self.assertLessEqual(empathy_score, 2)
        print(f'Low Empathy  -> {format_scores(result)}')

    def test_score_conversation_integration_low_clarity(self) -> None:
        """
        Test the full end-to-end scoring process with a low clarity conversation (structure may be normal).
        """
        low_clarity_path = self.base_path / 'dummy_conversation_low_clarity.json'
        conversation = load_conversation_data(low_clarity_path)
        with patch('app.connections.openai_client.ENABLE_AI', True):
            result = self.scoring_service.safe_score_conversation(conversation)

        self.assertIsInstance(result, ScoringResult)

        scores_dict = {s.metric.lower(): s.score for s in result.scoring.scores}
        clarity_score = scores_dict['clarity']
        self.assertIsNotNone(clarity_score, "Metric 'Clarity' not found in response.")
        self.assertLessEqual(clarity_score, 2)
        print(f'Low Clarity  -> {format_scores(result)}')

    def test_score_conversation_integration_low_structure(self) -> None:
        """
        Test the full end-to-end scoring process with a low structure conversation (clarity may be normal).
        """
        low_structure_path = self.base_path / 'dummy_conversation_low_structure.json'
        conversation = load_conversation_data(low_structure_path)
        with patch('app.connections.openai_client.ENABLE_AI', True):
            result = self.scoring_service.safe_score_conversation(conversation)

        self.assertIsInstance(result, ScoringResult)

        scores_dict = {s.metric.lower(): s.score for s in result.scoring.scores}
        structure_score = scores_dict['structure']
        self.assertIsNotNone(structure_score, "Metric 'Structure' not found in response.")
        self.assertLessEqual(structure_score, 2)
        print(f'Low Structure  -> {format_scores(result)}')

    def test_score_conversation_integration_low_focus(self) -> None:
        """
        Test the full end-to-end scoring process with a low focus conversation.
        """
        low_focus_path = self.base_path / 'dummy_conversation_low_focus.json'
        conversation = load_conversation_data(low_focus_path)
        with patch('app.connections.openai_client.ENABLE_AI', True):
            result = self.scoring_service.safe_score_conversation(conversation)

        self.assertIsInstance(result, ScoringResult)

        scores_dict = {s.metric.lower(): s.score for s in result.scoring.scores}
        focus_score = scores_dict['focus']

        self.assertIsNotNone(focus_score, "Metric 'Focus' not found in response.")
        self.assertLessEqual(focus_score, 2)
        print(f'Low Focus    -> {format_scores(result)}')

    def test_score_conversation_structure_1(self) -> None:
        structure_1_path = self.base_path / 'dummy_conversation_structure_1.json'
        conversation = load_conversation_data(structure_1_path)
        with patch('app.connections.openai_client.ENABLE_AI', True):
            result = self.scoring_service.safe_score_conversation(conversation)
        self.assertIsInstance(result, ScoringResult)
        scores_dict = {s.metric.lower(): s.score for s in result.scoring.scores}
        self.assertEqual(scores_dict['structure'], 1)
        print(f'Structure 1  -> {format_scores(result)}')

    def test_score_conversation_structure_2(self) -> None:
        structure_2_path = self.base_path / 'dummy_conversation_structure_2.json'
        conversation = load_conversation_data(structure_2_path)
        with patch('app.connections.openai_client.ENABLE_AI', True):
            result = self.scoring_service.safe_score_conversation(conversation)
        self.assertIsInstance(result, ScoringResult)
        scores_dict = {s.metric.lower(): s.score for s in result.scoring.scores}
        self.assertEqual(scores_dict['structure'], 2)
        print(f'Structure 2  -> {format_scores(result)}')

    def test_score_conversation_structure_3(self) -> None:
        structure_3_path = self.base_path / 'dummy_conversation_structure_3.json'
        conversation = load_conversation_data(structure_3_path)
        with patch('app.connections.openai_client.ENABLE_AI', True):
            result = self.scoring_service.safe_score_conversation(conversation)
        self.assertIsInstance(result, ScoringResult)
        scores_dict = {s.metric.lower(): s.score for s in result.scoring.scores}
        self.assertEqual(scores_dict['structure'], 3)
        print(f'Structure 3  -> {format_scores(result)}')

    def test_score_conversation_structure_4(self) -> None:
        structure_4_path = self.base_path / 'dummy_conversation_structure_4.json'
        conversation = load_conversation_data(structure_4_path)
        with patch('app.connections.openai_client.ENABLE_AI', True):
            result = self.scoring_service.safe_score_conversation(conversation)
        self.assertIsInstance(result, ScoringResult)
        scores_dict = {s.metric.lower(): s.score for s in result.scoring.scores}
        self.assertEqual(scores_dict['structure'], 4)
        print(f'Structure 4  -> {format_scores(result)}')

    def test_score_conversation_structure_5(self) -> None:
        structure_5_path = self.base_path / 'dummy_conversation_structure_5.json'
        conversation = load_conversation_data(structure_5_path)
        with patch('app.connections.openai_client.ENABLE_AI', True):
            result = self.scoring_service.safe_score_conversation(conversation)
        self.assertIsInstance(result, ScoringResult)
        scores_dict = {s.metric.lower(): s.score for s in result.scoring.scores}
        self.assertEqual(scores_dict['structure'], 5)
        print(f'Structure 5  -> {format_scores(result)}')


if __name__ == '__main__':
    unittest.main()
