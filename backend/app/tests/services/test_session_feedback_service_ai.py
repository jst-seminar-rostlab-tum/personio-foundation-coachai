import os
import time
import unittest
from unittest.mock import MagicMock, patch
from uuid import uuid4

from app.schemas.session_feedback import ExamplesRequest
from app.services.session_feedback.session_feedback_service import generate_and_store_feedback


@unittest.skipUnless(os.environ.get('RUN_AI_TESTS') == 'true', 'AI test not enabled')
class TestSessionFeedbackAI(unittest.TestCase):
    def test_scoring_real_ai_scoring_timing(self) -> None:
        mock_db_session = MagicMock()
        mock_db_session.add.return_value = None
        mock_db_session.commit.return_value = None
        mock_exec_result = MagicMock()
        mock_exec_result.first.return_value = None
        mock_db_session.exec.return_value = mock_exec_result

        example_request = ExamplesRequest(
            transcript=(
                'User: Hi, I noticed there has been some tension between us regarding the project'
                'timeline.\n'
                'Assistant: Yes, I felt that too. I think we have different expectations about'
                'deadlines.\n'
                'User: I want us to talk openly and find a way to collaborate better. Can you share'
                'your perspective?\n'
                'Assistant: I appreciate you bringing this up. I felt rushed, but I also could have'
                'communicated more clearly.\n'
                "User: Thank you for your honesty. Let's agree on clearer milestones and check-ins"
                'going forward.'
            ),
            objectives=[
                'Address the conflict directly',
                'Encourage open communication',
                'Find a collaborative solution',
            ],
            goal='Resolve a team conflict constructively',
            context='Team project deadline disagreement',
            other_party='Teammate',
            category='Conflict Resolution',
            key_concepts='Active listening, empathy, clear agreements',
        )
        session_id = uuid4()
        with (
            patch('app.connections.openai_client.ENABLE_AI', True),
            patch.multiple(
                'app.services.session_feedback.session_feedback_service',
                query_vector_db_and_prompt=lambda *a, **kw: '',
                safe_generate_training_examples=MagicMock(
                    positive_examples=[], negative_examples=[]
                ),
                safe_get_achieved_goals=MagicMock(goals_achieved=[]),
                safe_generate_recommendations=MagicMock(recommendations=[]),
            ),
        ):
            start = time.time()
            feedback = generate_and_store_feedback(
                session_id=session_id,
                example_request=example_request,
                db_session=mock_db_session,
            )
            end = time.time()
            print('\n================= AI Scoring Result =================')
            print(f'Elapsed time: {end - start:.2f} seconds')
            print(f'Scores: {feedback.scores}')
            print(f'Overall score: {feedback.overall_score}')
            print(f'Status: {feedback.status}')
            print('====================================================\n')


if __name__ == '__main__':
    unittest.main()
