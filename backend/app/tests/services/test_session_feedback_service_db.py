import unittest
from collections.abc import Generator
from datetime import datetime
from typing import Any
from unittest.mock import MagicMock, patch
from uuid import uuid4

from sqlmodel import Session as DBSession
from sqlmodel import SQLModel, create_engine, select

from app.enums.conversation_scenario_status import ConversationScenarioStatus
from app.enums.feedback_status import FeedbackStatus
from app.enums.language import LanguageCode
from app.enums.session_status import SessionStatus
from app.enums.speaker import SpeakerType
from app.models.admin_dashboard_stats import AdminDashboardStats
from app.models.conversation_scenario import ConversationScenario
from app.models.session import Session
from app.models.session_turn import SessionTurn
from app.models.user_profile import UserProfile
from app.schemas.conversation_scenario import ConversationScenarioRead
from app.schemas.session_feedback import (
    FeedbackCreate,
    GoalsAchievedRead,
    NegativeExample,
    PositiveExample,
    Recommendation,
    RecommendationsRead,
    SessionExamplesRead,
)
from app.schemas.session_turn import SessionTurnStitchAudioSuccess
from app.services.session_feedback.session_feedback_service import (
    generate_and_store_feedback,
    get_conversation_data,
)


# Inject mock scoring_service
class MockScore:
    def __init__(self, metric: str, score: float) -> None:
        self.metric = metric
        self.score = score


class MockScoringRead:
    class Scoring:
        def __init__(self, with_data: bool | None) -> None:
            if with_data:
                self.scores = [
                    MockScore('structure', 4),
                    MockScore('empathy', 5),
                    MockScore('focus', 3),
                    MockScore('clarity', 4),
                ]
                self.overall_score = 16.0
            else:
                self.scores = []
                self.overall_score = 0

    def __init__(self, with_data: bool | None = None) -> None:
        self.scoring = self.Scoring(with_data)


class FakeGCS:
    def __init__(self) -> None:
        pass

    def generate_signed_url(self, filename: str) -> str:
        return f'https://example.com/{filename}'

    def document_exists(self, filename: str) -> bool:
        # Simulate that the document exists for testing purposes
        return True


class TestSessionFeedbackService(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.engine = create_engine('sqlite:///:memory:')
        SQLModel.metadata.create_all(cls.engine)
        cls.SessionLocal = DBSession(cls.engine)

    def setUp(self) -> None:
        self.session = self.SessionLocal
        self.mock_advisor_service = MagicMock()
        self.mock_background_tasks = MagicMock()
        self.mock_user_profile = UserProfile(
            full_name='Mock User',
            email='mock@example.com',
            phone_number='1234567890',
            total_sessions=1,
        )
        self.gcs_audio_global_patcher = patch(
            'app.connections.gcs_client._gcs_audio_manager', new=FakeGCS()
        )
        self.gcs_audio_global_patcher.start()

    def tearDown(self) -> None:
        self.session.rollback()
        self.gcs_audio_global_patcher.stop()

    def insert_minimal_conversation(self) -> dict:
        scenario_id = uuid4()
        user = self.session.exec(select(UserProfile)).first()
        # delete user if exists --> email+phone have to be unique
        if user:
            self.session.delete(user)
            self.session.commit()
        user_id = uuid4()
        self.session.add(
            UserProfile(
                id=user_id,
                full_name='Test',
                email='a@b.com',
                phone_number='123',
                preferred_language_code=LanguageCode.en,
                total_sessions=1,
            )
        )
        scenario = ConversationScenario(
            id=scenario_id,
            user_id=user_id,
            category_id='feedback',
            language_code=LanguageCode.en,
            status=ConversationScenarioStatus.ready,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            persona_name='Test Persona',
            persona='',
            situational_facts='Feedback context',
        )
        self.session.add(scenario)
        session_id = uuid4()
        session_obj = Session(
            id=session_id,
            scenario_id=scenario_id,
            status=SessionStatus.started,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.session.add(session_obj)
        turn = SessionTurn(
            id=uuid4(),
            session_id=session_id,
            speaker=SpeakerType.user,
            start_offset_ms=0,
            end_offset_ms=1000,
            text='Hello, Sam!',
            audio_uri='',
            ai_emotion='neutral',
            created_at=datetime.now(),
        )
        self.session.add(turn)
        self.session.commit()
        return {'session_id': session_id, 'user_id': user_id}

    def test_get_conversation_data(self) -> None:
        data = self.insert_minimal_conversation()
        session_id = data['session_id']
        conversation = get_conversation_data(self.session, session_id)
        self.assertIsInstance(conversation, ConversationScenarioRead)
        self.assertEqual(conversation.scenario.situational_facts, 'Feedback context')
        self.assertEqual(len(conversation.transcript), 1)
        self.assertEqual(conversation.transcript[0].text, 'Hello, Sam!')
        self.assertEqual(conversation.transcript[0].speaker, SpeakerType.user)

    @patch('app.services.session_feedback.session_feedback_llm.generate_training_examples')
    @patch('app.services.session_feedback.session_feedback_llm.get_achieved_goals')
    @patch('app.services.session_feedback.session_feedback_llm.generate_recommendations')
    def test_generate_and_store_feedback(
        self,
        mock_recommendations: MagicMock,
        mock_goals: MagicMock,
        mock_examples: MagicMock,
    ) -> None:
        data = self.insert_minimal_conversation()
        session_id = data['session_id']
        mock_examples.return_value = SessionExamplesRead(
            positive_examples=[
                PositiveExample(
                    heading='Clear Objective Addressed',
                    feedback='The user successfully summarized the objective.',
                    quote='I want to make sure we both feel heard and find a solution together.',
                )
            ],
            negative_examples=[
                NegativeExample(
                    heading='Missed Empathy',
                    feedback="The user dismissed the other party's concern.",
                    quote="That's not important right now.",
                    improved_quote="I understand your concern—let's come back to it in a moment.",
                )
            ],
        )
        mock_goals.return_value = GoalsAchievedRead(goals_achieved=['G1', 'G2'])
        mock_recommendations.return_value = RecommendationsRead(
            recommendations=[
                Recommendation(
                    heading='Practice the STAR method',
                    recommendation='When giving feedback, use the Situation, Task, '
                    'Action, Result framework to ' + 'provide more concrete examples.',
                ),
                Recommendation(
                    heading='Ask more diagnostic questions',
                    recommendation='Spend more time understanding root causes before moving '
                    + 'to solutions. This builds empathy and leads to more effective outcomes.',
                ),
                Recommendation(
                    heading='Define clear next steps',
                    recommendation='End feedback conversations with agreed-upon action items, '
                    + 'timelines, and follow-up plans.',
                ),
            ]
        )

        mock_scoring_service = MagicMock()
        mock_scoring_service.safe_score_conversation.return_value = MockScoringRead(with_data=True)

        mock_session_turn_service = MagicMock()
        mock_session_turn_service.stitch_mp3s_from_gcs.return_value = SessionTurnStitchAudioSuccess(
            output_filename='mock_audio_uri.mp3',
            audio_duration_s=120,
        )
        example_request = FeedbackCreate(
            transcript='Sample transcript...',
            objectives=['Obj1', 'Obj2'],
            persona='**Name**: Someone\n**Training Focus**: Goal',
            situational_facts='Context',
            category='Feedback',
            key_concepts='KC1',
        )
        # mock_session_generator_func = MagicMock()

        def mock_session_generator_func() -> Generator[Any, None, None]:
            yield self.session

        feedback = generate_and_store_feedback(
            session_id=session_id,
            feedback_request=example_request,
            background_tasks=self.mock_background_tasks,
            user_profile_id=uuid4(),
            scoring_service=mock_scoring_service,
            session_turn_service=mock_session_turn_service,
            advisor_service=self.mock_advisor_service,
            session_generator_func=mock_session_generator_func,
        )

        self.assertEqual(feedback.session_id, session_id)
        self.assertEqual(feedback.goals_achieved, ['G1', 'G2'])

        self.assertEqual(len(feedback.example_positive), 1)
        self.assertEqual(feedback.example_positive[0]['heading'], 'Clear Objective Addressed')
        self.assertEqual(
            feedback.example_positive[0]['quote'],
            'I want to make sure we both feel heard and find a solution together.',
        )
        self.assertEqual(feedback.example_negative[0]['heading'], 'Missed Empathy')
        self.assertEqual(feedback.example_negative[0]['quote'], "That's not important right now.")
        self.assertEqual(
            feedback.example_negative[0]['improved_quote'],
            "I understand your concern—let's come back to it in a moment.",
        )
        self.assertEqual(len(feedback.recommendations), 3)
        self.assertEqual(feedback.recommendations[0]['heading'], 'Practice the STAR method')
        self.assertEqual(
            feedback.recommendations[0]['recommendation'],
            'When giving feedback, use the Situation, Task, Action, '
            'Result framework to provide more concrete examples.',
        )
        self.assertEqual(feedback.recommendations[1]['heading'], 'Ask more diagnostic questions')
        self.assertEqual(
            feedback.recommendations[1]['recommendation'],
            'Spend more time understanding root causes before moving to '
            'solutions. This builds empathy and leads to more effective outcomes.',
        )
        self.assertEqual(feedback.recommendations[2]['heading'], 'Define clear next steps')
        self.assertEqual(
            feedback.recommendations[2]['recommendation'],
            'End feedback conversations with agreed-upon action'
            ' items, timelines, and follow-up plans.',
        )
        self.assertEqual(feedback.status, FeedbackStatus.completed)
        self.assertIsNotNone(feedback.created_at)
        self.assertIsNotNone(feedback.updated_at)

    @patch('app.services.session_feedback.session_feedback_llm.generate_training_examples')
    @patch('app.services.session_feedback.session_feedback_llm.get_achieved_goals')
    @patch('app.services.session_feedback.session_feedback_llm.generate_recommendations')
    def test_generate_and_store_feedback_with_errors(
        self,
        mock_recommendations: MagicMock,
        mock_goals: MagicMock,
        mock_examples: MagicMock,
    ) -> None:
        data = self.insert_minimal_conversation()
        session_id = data['session_id']
        mock_examples.side_effect = Exception('Failed to generate examples')

        mock_goals.return_value = GoalsAchievedRead(goals_achieved=['G1'])
        mock_recommendations.return_value = RecommendationsRead(
            recommendations=[
                Recommendation(
                    heading='Some heading',
                    recommendation='Some text',
                )
            ]
        )

        mock_scoring_service = MagicMock()
        mock_scoring_service.safe_score_conversation.return_value = MockScoringRead()

        mock_session_turn_service = MagicMock()
        mock_session_turn_service.stitch_mp3s_from_gcs.return_value = SessionTurnStitchAudioSuccess(
            output_filename='mock_audio_uri.mp3',
            audio_duration_s=120,
        )
        example_request = FeedbackCreate(
            transcript='Error case transcript...',
            objectives=['ObjX'],
            persona='**Name**: Other\n**Training Focus**: Goal',
            situational_facts='Context',
            category='Category',
            key_concepts='KeyConcept',
        )

        def mock_session_generator_func() -> Generator[Any, None, None]:
            yield self.session

        feedback = generate_and_store_feedback(
            session_id=session_id,
            feedback_request=example_request,
            background_tasks=self.mock_background_tasks,
            user_profile_id=uuid4(),
            scoring_service=mock_scoring_service,
            session_turn_service=mock_session_turn_service,
            advisor_service=self.mock_advisor_service,
            session_generator_func=mock_session_generator_func,
        )

        self.assertEqual(feedback.status, FeedbackStatus.failed)
        self.assertEqual(feedback.goals_achieved, ['G1'])
        self.assertEqual(len(feedback.example_positive), 0)
        self.assertEqual(len(feedback.recommendations), 1)
        self.assertEqual(len(feedback.goals_achieved), 1)
        self.assertEqual(len(feedback.example_positive), 0)
        self.assertEqual(len(feedback.recommendations), 1)
        self.assertEqual(feedback.recommendations[0]['heading'], 'Some heading')
        self.assertEqual(feedback.recommendations[0]['recommendation'], 'Some text')

        self.assertIsNotNone(feedback.created_at)
        self.assertIsNotNone(feedback.updated_at)

        self.assertEqual(feedback.overall_score, 0)

    @patch('app.services.session_feedback.session_feedback_llm.generate_training_examples')
    @patch('app.services.session_feedback.session_feedback_llm.get_achieved_goals')
    @patch('app.services.session_feedback.session_feedback_llm.generate_recommendations')
    def test_scoring_and_stats_update(
        self,
        mock_recommendations: MagicMock,
        mock_goals: MagicMock,
        mock_examples: MagicMock,
    ) -> None:
        # Mock AI scoring
        mock_examples.return_value = SessionExamplesRead(positive_examples=[], negative_examples=[])
        mock_goals.return_value = GoalsAchievedRead(goals_achieved=[])
        mock_recommendations.return_value = RecommendationsRead(recommendations=[])

        mock_scoring_service = MagicMock()
        mock_scoring_service.safe_score_conversation.return_value = MockScoringRead(with_data=True)

        mock_session_turn_service = MagicMock()
        mock_session_turn_service.stitch_mp3s_from_gcs.return_value = SessionTurnStitchAudioSuccess(
            output_filename='mock_audio_uri.mp3',
            audio_duration_s=120,
        )
        data = self.insert_minimal_conversation()

        user_id = data['user_id']
        session_id = data['session_id']

        self.session.add(AdminDashboardStats())
        self.session.commit()

        example_request = FeedbackCreate(
            transcript='Sample transcript...',
            objectives=['Obj1', 'Obj2'],
            persona='**Name**: Someone\n**Training Focus**: Goal',
            situational_facts='Context',
            category='Feedback',
            key_concepts='KC1',
        )

        def mock_session_generator_func() -> Generator[Any, None, None]:
            yield self.session

        feedback = generate_and_store_feedback(
            session_id=session_id,
            feedback_request=example_request,
            background_tasks=self.mock_background_tasks,
            user_profile_id=uuid4(),
            scoring_service=mock_scoring_service,
            session_turn_service=mock_session_turn_service,
            advisor_service=self.mock_advisor_service,
            session_generator_func=mock_session_generator_func,
        )
        # Check feedback score structure
        self.assertDictEqual(
            feedback.scores, {'structure': 4, 'empathy': 5, 'focus': 3, 'clarity': 4}
        )
        self.assertEqual(feedback.overall_score, 16.0)
        # Check user_profile statistics
        user = self.session.get(UserProfile, user_id)
        self.assertIsNotNone(user)
        self.assertEqual(user.score_sum, 16.0)
        # Check admin_dashboard_stats statistics
        stats = self.session.exec(select(AdminDashboardStats)).first()
        self.assertIsNotNone(stats)
        self.assertEqual(stats.score_sum, 16.0)
        self.assertEqual(stats.total_trainings, 1)
        # Check average score
        self.assertAlmostEqual(user.score_sum / user.total_sessions, 16.0)
        self.assertAlmostEqual(stats.score_sum / stats.total_trainings, 16.0)


if __name__ == '__main__':
    unittest.main()
