import os
import time
import unittest
from datetime import datetime
from unittest.mock import patch
from uuid import uuid4

from app.enums.language import LanguageCode
from app.enums.speaker import SpeakerType
from app.models.conversation_scenario import ConversationScenarioStatus, DifficultyLevel
from app.schemas.conversation_scenario import (
    ConversationScenario,
    ConversationScenarioWithTranscript,
)
from app.schemas.session_turn import SessionTurnRead
from app.services.scoring_service import scoring_service


@unittest.skipUnless(os.environ.get('RUN_AI_TESTS') == 'true', 'AI test not enabled')
class TestSessionFeedbackAI(unittest.TestCase):
    def test_scoring_real_ai_scoring_timing(self) -> None:
        scenario = ConversationScenario(
            id=uuid4(),
            user_id=uuid4(),
            category_id='feedback',
            custom_category_label=None,
            difficulty_level=DifficultyLevel.medium,
            language_code=LanguageCode.en,
            status=ConversationScenarioStatus.ready,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            persona='',
            situational_facts='',
        )
        transcript = [
            SessionTurnRead(
                id=uuid4(),
                speaker=SpeakerType.user,
                full_audio_start_offset_ms=0,
                text="Hi Sam, let's talk about the project communication.",
                ai_emotion='neutral',
                created_at=datetime.now(),
            ),
            SessionTurnRead(
                id=uuid4(),
                speaker=SpeakerType.assistant,
                full_audio_start_offset_ms=2000,
                text='Sure, I think there were some misunderstandings about the deadlines.',
                ai_emotion='neutral',
                created_at=datetime.now(),
            ),
            SessionTurnRead(
                id=uuid4(),
                speaker=SpeakerType.user,
                full_audio_start_offset_ms=4000,
                text="Yes, let's clarify expectations and improve our communication going forward.",
                ai_emotion='neutral',
                created_at=datetime.now(),
            ),
        ]
        conversation = ConversationScenarioWithTranscript(
            scenario=scenario,
            transcript=transcript,
        )
        with patch('app.connections.openai_client.ENABLE_AI', True):
            start = time.time()
            result = scoring_service.score_conversation(conversation)
            end = time.time()
            print('\n================= AI Scoring Result =================')
            print(f'Elapsed time: {end - start:.2f} seconds')
            print(f'Overall Scoring: {result.scoring.overall_score}')
            for score in result.scoring.scores:
                print(f'{score.metric}: {score.score} - {score.justification}')
            print(f'Summary: {result.conversation_summary}')
            print('====================================================\n')


if __name__ == '__main__':
    unittest.main()
