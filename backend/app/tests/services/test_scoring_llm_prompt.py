# ruff: noqa: E501
import json
import os
import unittest
import uuid
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from app.connections.gcs_client import get_gcs_audio_manager
from app.enums.language import LanguageCode
from app.models.conversation_scenario import ConversationScenarioStatus, DifficultyLevel
from app.schemas.conversation_scenario import (
    ConversationScenario,
    ConversationScenarioRead,
)
from app.schemas.scoring_schema import ScoringRead
from app.schemas.session_turn import SessionTurnRead, SpeakerType
from app.services.scoring_service import ScoringService


def format_scores(result: ScoringRead) -> str:
    """Helper function to format all metric scores for printing."""
    scores = {s.metric: s.score for s in result.scoring.scores}
    return (
        f'Overall: {result.scoring.overall_score:.2f} | '
        f'Structure: {scores["structure"]} | '
        f'Empathy: {scores["empathy"]} | '
        f'Focus: {scores["focus"]} | '
        f'Clarity: {scores["clarity"]}'
    )


def load_conversation_data(json_path: Path) -> ConversationScenarioRead:
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)
    # scenario
    scenario = ConversationScenario(**data['scenario'])
    # transcript
    transcript = [SessionTurnRead(**turn) for turn in data['transcript']]
    return ConversationScenarioRead(scenario=scenario, transcript=transcript)


TEST_TRANSCRIPT = 'User: Hello, thank you for meeting with me today. I’d like to discuss your recent performance and see how I can support you.'


@unittest.skipUnless(os.environ.get('RUN_AI_TESTS') == 'true', 'AI test not enabled')
class TestScoringServiceIntegration(unittest.TestCase):
    def setUp(self) -> None:
        """Set up the scoring service for an integration test."""
        self.base_path = Path(__file__).parent.parent.parent / 'data'
        self.rubric_path = self.base_path / 'conversation_rubric.json'
        self.scoring_service = ScoringService(rubric_path=self.rubric_path)
        # Patch GCS audio manager to always return local file url
        patcher = patch('app.connections.gcs_client.get_gcs_audio_manager')
        self.mock_gcs_manager = patcher.start()
        self.addCleanup(patcher.stop)

        def fake_generate_signed_url(filename: str) -> str:
            return f'file://{os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/audio/{filename}"))}'

        self.mock_gcs_manager.return_value.generate_signed_url.side_effect = (
            fake_generate_signed_url
        )

    def test_score_conversation_integration_good_example(self) -> None:
        """
        Test the full end-to-end scoring process with a good conversation example.
        """
        good_conversation_path = self.base_path / 'dummy_conversation_good_example.json'
        conversation = load_conversation_data(good_conversation_path)
        with patch('app.connections.openai_client.ENABLE_AI', True):
            result = self.scoring_service.safe_score_conversation(conversation)

        self.assertIsInstance(result, ScoringRead)
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

        self.assertIsInstance(result, ScoringRead)

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
            result = self.scoring_service.score_conversation(conversation)

        self.assertIsInstance(result, ScoringRead)

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

        self.assertIsInstance(result, ScoringRead)

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

        self.assertIsInstance(result, ScoringRead)

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
        print('==== LLM structure output(structure_1) ====')
        print(result.model_dump_json(indent=2))
        print('==== LLM structure output(structure_1)end ====')
        self.assertIsInstance(result, ScoringRead)
        scores_dict = {s.metric.lower(): s.score for s in result.scoring.scores}
        expected = 1
        tolerance = 1
        self.assertTrue(
            abs(scores_dict['structure'] - expected) <= tolerance,
            f'Structure score {scores_dict["structure"]} not within ±{tolerance} of expected {expected}',
        )

    def test_score_conversation_structure_2(self) -> None:
        structure_2_path = self.base_path / 'dummy_conversation_structure_2.json'
        conversation = load_conversation_data(structure_2_path)
        with patch('app.connections.openai_client.ENABLE_AI', True):
            result = self.scoring_service.safe_score_conversation(conversation)
        print('==== LLM structure output(structure_2) ====')
        print(result.model_dump_json(indent=2))
        print('==== LLM structure output(structure_2)end ====')
        self.assertIsInstance(result, ScoringRead)
        scores_dict = {s.metric.lower(): s.score for s in result.scoring.scores}
        expected = 2
        tolerance = 1
        self.assertTrue(
            abs(scores_dict['structure'] - expected) <= tolerance,
            f'Structure score {scores_dict["structure"]} not within ±{tolerance} of expected {expected}',
        )

    def test_score_conversation_structure_3(self) -> None:
        structure_3_path = self.base_path / 'dummy_conversation_structure_3.json'
        conversation = load_conversation_data(structure_3_path)
        with patch('app.connections.openai_client.ENABLE_AI', True):
            result = self.scoring_service.safe_score_conversation(conversation)
        print('==== LLM structure output(structure_3) ====')
        print(result.model_dump_json(indent=2))
        print('==== LLM structure output(structure_3)end ====')
        self.assertIsInstance(result, ScoringRead)
        scores_dict = {s.metric.lower(): s.score for s in result.scoring.scores}
        expected = 3
        tolerance = 1
        self.assertTrue(
            abs(scores_dict['structure'] - expected) <= tolerance,
            f'Structure score {scores_dict["structure"]} not within ±{tolerance} of expected {expected}',
        )

    def test_score_conversation_structure_4(self) -> None:
        structure_4_path = self.base_path / 'dummy_conversation_structure_4.json'
        conversation = load_conversation_data(structure_4_path)
        with patch('app.connections.openai_client.ENABLE_AI', True):
            result = self.scoring_service.safe_score_conversation(conversation)
        print('==== LLM structure output(structure_4) ====')
        print(result.model_dump_json(indent=2))
        print('==== LLM structure output(structure_4)end ====')
        self.assertIsInstance(result, ScoringRead)
        scores_dict = {s.metric.lower(): s.score for s in result.scoring.scores}
        expected = 4
        tolerance = 1
        self.assertTrue(
            abs(scores_dict['structure'] - expected) <= tolerance,
            f'Structure score {scores_dict["structure"]} not within ±{tolerance} of expected {expected}',
        )

    def test_score_conversation_structure_5(self) -> None:
        structure_5_path = self.base_path / 'dummy_conversation_structure_5.json'
        conversation = load_conversation_data(structure_5_path)
        with patch('app.connections.openai_client.ENABLE_AI', True):
            result = self.scoring_service.safe_score_conversation(conversation)
        self.assertIsInstance(result, ScoringRead)
        print('==== LLM structure output(structure_5) ====')
        print(result.model_dump_json(indent=2))
        print('==== LLM structure output(structure_5)end ====')
        self.assertIsInstance(result, ScoringRead)
        scores_dict = {s.metric.lower(): s.score for s in result.scoring.scores}
        expected = 5
        tolerance = 1
        self.assertTrue(
            abs(scores_dict['structure'] - expected) <= tolerance,
            f'Structure score {scores_dict["structure"]} not within ±{tolerance} of expected {expected}',
        )

    def test_score_conversation_with_various_audios(self) -> None:
        """
        Test the full end-to-end scoring process with various audio.
        """

        audio_files = ['standard.mp3', 'playful.mp3', 'excited.mp3', 'strong_expressive.mp3']
        conversation = ConversationScenarioRead(
            scenario=ConversationScenario(
                id=uuid.uuid4(),
                user_id=uuid.uuid4(),
                category_id='feedback',
                custom_category_label=None,
                language_code=LanguageCode.en,
                persona_name='',
                persona='',
                situational_facts='',
                difficulty_level=DifficultyLevel.medium,
                status=ConversationScenarioStatus.ready,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
            transcript=[
                SessionTurnRead(
                    id=uuid.uuid4(),
                    speaker=SpeakerType.user,
                    text=TEST_TRANSCRIPT,
                    ai_emotion=None,
                    created_at=datetime.now(),
                    full_audio_start_offset_ms=0,
                )
            ],
        )
        for audio_file in audio_files:
            audio_uri = get_gcs_audio_manager().generate_signed_url(audio_file)
            print(f'\n==== Testing with audio: {audio_file} ====')
            try:
                result = self.scoring_service.score_conversation(
                    conversation,
                    audio_uri=audio_uri,
                )
                print(result.model_dump_json(indent=2))
            except Exception as e:
                print(f'Error with {audio_file}: {e}')


if __name__ == '__main__':
    unittest.main()
