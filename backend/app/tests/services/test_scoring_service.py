import json
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch
from uuid import uuid4

from pydantic import ValidationError

from app.models.conversation_scenario import ConversationScenarioStatus, DifficultyLevel
from app.models.language import LanguageCode
from app.models.session_turn import SpeakerEnum
from app.schemas.conversation_scenario import (
    ConversationScenario,
    ConversationScenarioRead,
)
from app.schemas.scoring_schema import ConversationScore, MetricScore, ScoringResult
from app.schemas.session_turn import SessionTurnRead
from app.services.scoring_service import ScoringService


class TestScoringService(unittest.TestCase):
    def setUp(self) -> None:
        self.test_data_dir = Path(__file__).parent / 'test_data'
        self.test_data_dir.mkdir(exist_ok=True)
        self.rubric_path = self.test_data_dir / 'test_rubric.json'
        with open(self.rubric_path, 'w') as f:
            json.dump({'title': 'Test Rubric'}, f)
        self.scenario = ConversationScenario(
            id=uuid4(),
            user_id=uuid4(),
            category_id='feedback',
            custom_category_label=None,
            persona='',
            situational_facts='',
            difficulty_level=DifficultyLevel.medium,
            language_code=LanguageCode.en,
            status=ConversationScenarioStatus.ready,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.transcript = [
            SessionTurnRead(
                id=uuid4(),
                session_id=uuid4(),
                speaker=SpeakerEnum.user,
                start_offset_ms=0,
                end_offset_ms=1000,
                text='Hello',
                audio_uri='',
                ai_emotion='neutral',
                created_at=datetime(2024, 6, 28, 10, 0, 1),
            )
        ]
        self.conversation = ConversationScenarioRead(
            scenario=self.scenario, transcript=self.transcript
        )
        self.scoring_service = ScoringService(rubric_path=self.rubric_path)

    def tearDown(self) -> None:
        if self.rubric_path.exists():
            self.rubric_path.unlink()
        if self.test_data_dir.exists():
            self.test_data_dir.rmdir()

    def test_initialization(self) -> None:
        self.assertIsNotNone(self.scoring_service.rubric)
        self.assertEqual(self.scoring_service.rubric['title'], 'Test Rubric')

    @patch('app.services.scoring_service.call_structured_llm')
    def test_score_conversation_calls_llm_and_returns_valid_structure(
        self, mock_call_structured_llm: MagicMock
    ) -> None:
        mock_result = ScoringResult(
            conversation_summary='The User initiated the conversation clearly'
            + 'and maintained a professional tone.',
            scoring=ConversationScore(
                overall_score=4.25,
                scores=[
                    MetricScore(metric='structure', score=5, justification='Perfect.'),
                    MetricScore(metric='empathy', score=4, justification='Good.'),
                    MetricScore(metric='focus', score=4, justification='Good.'),
                    MetricScore(metric='clarity', score=4, justification='Good.'),
                ],
            ),
        )
        mock_call_structured_llm.return_value = mock_result
        result = self.scoring_service.score_conversation(self.conversation)
        mock_call_structured_llm.assert_called_once()
        _, kwargs = mock_call_structured_llm.call_args
        self.assertIn('request_prompt', kwargs)
        self.assertEqual(kwargs['output_model'], ScoringResult)
        self.assertEqual(result, mock_result)
        self.assertEqual(result.scoring.overall_score, 4.25)
        self.assertEqual(len(result.scoring.scores), 4)

    def test_build_prompt(self) -> None:
        system_prompt = self.scoring_service._build_system_prompt()
        user_prompt = self.scoring_service._build_user_prompt(self.conversation)
        self.assertIn('Test Rubric', system_prompt)
        self.assertIn('**Conversation Scenario:**\n', user_prompt)
        self.assertIn('provide a score from 1 to 5 for each metric', user_prompt)
        print(user_prompt)

    def test_rubric_to_markdown_real_rubric(self) -> None:
        real_rubric_path = Path(__file__).parent.parent.parent / 'data' / 'conversation_rubric.json'
        self.scoring_service.rubric = self.scoring_service._load_json(real_rubric_path)
        md = self.scoring_service.rubric_to_markdown()
        self.assertIn('# Conversation Quality Rubric', md)
        self.assertIn('A rubric for scoring conversation quality', md)
        self.assertIn('## Structure', md)
        self.assertIn('## Empathy', md)
        self.assertIn('## Focus', md)
        self.assertIn('## Clarity', md)
        self.assertIn('## Common Levels', md)
        self.assertIn('- **Score 0**: Complete failure to demonstrate the skill.', md)

    def test_metric_score_out_of_range(self) -> None:
        with self.assertRaises(ValidationError):
            MetricScore(metric='structure', score=0, justification='Too low')
        with self.assertRaises(ValidationError):
            MetricScore(metric='structure', score=6, justification='Too high')
        with self.assertRaises(ValidationError):
            MetricScore(metric='structure', score=3.5, justification='Not int')


if __name__ == '__main__':
    unittest.main()
