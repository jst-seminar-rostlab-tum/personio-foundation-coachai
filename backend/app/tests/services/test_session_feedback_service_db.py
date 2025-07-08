import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch
from uuid import UUID, uuid4

from sqlmodel import Session as DBSession
from sqlmodel import SQLModel, create_engine, select

from app.models import FeedbackStatusEnum
from app.models.conversation_scenario import (
    ConversationScenario,
    ConversationScenarioStatus,
)
from app.models.language import LanguageCode
from app.models.session import Session, SessionStatus
from app.models.session_turn import SessionTurn, SpeakerEnum
from app.schemas.conversation_scenario import ConversationScenarioRead
from app.schemas.session_feedback import (
    FeedbackRequest,
    GoalsAchievedCollection,
    NegativeExample,
    PositiveExample,
    Recommendation,
    RecommendationsCollection,
    SessionExamplesCollection,
)
from app.services.session_feedback.session_feedback_service import (
    generate_and_store_feedback,
    get_conversation_data,
)


class TestSessionFeedbackService(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.engine = create_engine('sqlite:///:memory:')
        SQLModel.metadata.create_all(cls.engine)
        cls.SessionLocal = DBSession(cls.engine)

    def setUp(self) -> None:
        self.session = self.SessionLocal

    def tearDown(self) -> None:
        self.session.rollback()

    def insert_minimal_conversation(self) -> UUID:
        scenario_id = uuid4()
        user_id = uuid4()
        scenario = ConversationScenario(
            id=scenario_id,
            user_id=user_id,
            category_id='feedback',
            language_code=LanguageCode.en,
            status=ConversationScenarioStatus.ready,
            created_at=datetime.now(),
            updated_at=datetime.now(),
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
            speaker=SpeakerEnum.user,
            start_offset_ms=0,
            end_offset_ms=1000,
            text='Hello, Sam!',
            audio_uri='',
            ai_emotion='neutral',
            created_at=datetime.now(),
        )
        self.session.add(turn)
        self.session.commit()
        return session_id

    def test_get_conversation_data(self) -> None:
        session_id = self.insert_minimal_conversation()
        conversation = get_conversation_data(self.session, session_id)
        self.assertIsInstance(conversation, ConversationScenarioRead)
        self.assertEqual(conversation.scenario.situational_facts, 'Feedback context')
        self.assertEqual(len(conversation.transcript), 1)
        self.assertEqual(conversation.transcript[0].text, 'Hello, Sam!')
        self.assertEqual(conversation.transcript[0].speaker, SpeakerEnum.user)

    @patch('app.services.session_feedback.session_feedback_llm.generate_training_examples')
    @patch('app.services.session_feedback.session_feedback_llm.get_achieved_goals')
    @patch('app.services.session_feedback.session_feedback_llm.generate_recommendations')
    def test_generate_and_store_feedback(
        self,
        mock_recommendations: MagicMock,
        mock_goals: MagicMock,
        mock_examples: MagicMock,
    ) -> None:
        session_id = self.insert_minimal_conversation()
        mock_examples.return_value = SessionExamplesCollection(
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
        mock_goals.return_value = GoalsAchievedCollection(goals_achieved=['G1', 'G2'])
        mock_recommendations.return_value = RecommendationsCollection(
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

        # Inject mock scoring_service
        class MockScore:
            def __init__(self, metric: str, score: float) -> None:
                self.metric = metric
                self.score = score

        class MockScoringResult:
            class Scoring:
                def __init__(self) -> None:
                    self.scores = [
                        MockScore('structure', 4),
                        MockScore('empathy', 5),
                        MockScore('focus', 3),
                        MockScore('clarity', 4),
                    ]
                    self.overall_score = 4.0

            def __init__(self) -> None:
                self.scoring = self.Scoring()

        mock_scoring_service = MagicMock()
        mock_scoring_service.score_conversation.return_value = MockScoringResult()

        mock_session_turn_service = MagicMock()
        mock_session_turn_service.stitch_mp3s_from_gcs.return_value = 'mock_audio_uri.mp3'

        example_request = FeedbackRequest(
            transcript='Sample transcript...',
            objectives=['Obj1', 'Obj2'],
            persona='**Name**: Someone\n**Training Focus**: Goal',
            situational_facts='Context',
            category='Feedback',
            key_concepts='KC1',
        )

        feedback = generate_and_store_feedback(
            session_id=session_id,
            feedback_request=example_request,
            db_session=self.session,
            scoring_service=mock_scoring_service,
            session_turn_service=mock_session_turn_service,
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
        self.assertEqual(feedback.status, FeedbackStatusEnum.completed)
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
        session_id = self.insert_minimal_conversation()
        mock_examples.side_effect = Exception('Failed to generate examples')

        mock_goals.return_value = GoalsAchievedCollection(goals_achieved=['G1'])
        mock_recommendations.return_value = RecommendationsCollection(
            recommendations=[
                Recommendation(
                    heading='Some heading',
                    recommendation='Some text',
                )
            ]
        )

        # mock scoring_service
        class MockScoringResult:
            class Scoring:
                def __init__(self) -> None:
                    self.scores = []
                    self.overall_score = 0

            def __init__(self) -> None:
                self.scoring = self.Scoring()

        mock_scoring_service = MagicMock()
        mock_scoring_service.score_conversation.return_value = MockScoringResult()

        mock_session_turn_service = MagicMock()
        mock_session_turn_service.stitch_mp3s_from_gcs.return_value = 'mock_audio_uri.mp3'

        example_request = FeedbackRequest(
            transcript='Error case transcript...',
            objectives=['ObjX'],
            persona='**Name**: Other\n**Training Focus**: Goal',
            situational_facts='Context',
            category='Category',
            key_concepts='KeyConcept',
        )

        feedback = generate_and_store_feedback(
            session_id=session_id,
            feedback_request=example_request,
            db_session=self.session,
            scoring_service=mock_scoring_service,
            session_turn_service=mock_session_turn_service,
        )

        self.assertEqual(feedback.status, FeedbackStatusEnum.failed)
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
        self.assertEqual(feedback.transcript_uri, '')

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
        mock_examples.return_value = SessionExamplesCollection(
            positive_examples=[], negative_examples=[]
        )
        mock_goals.return_value = GoalsAchievedCollection(goals_achieved=[])
        mock_recommendations.return_value = RecommendationsCollection(recommendations=[])

        # Mock scoring_service
        class MockScore:
            def __init__(self, metric: str, score: float) -> None:
                self.metric = metric
                self.score = score

        class MockScoringResult:
            class Scoring:
                def __init__(self) -> None:
                    self.scores = [
                        MockScore('structure', 4),
                        MockScore('empathy', 5),
                        MockScore('focus', 3),
                        MockScore('clarity', 4),
                    ]
                    self.overall_score = 4.0

            def __init__(self) -> None:
                self.scoring = self.Scoring()

        mock_scoring_service = MagicMock()
        mock_scoring_service.score_conversation.return_value = MockScoringResult()

        mock_session_turn_service = MagicMock()
        mock_session_turn_service.stitch_mp3s_from_gcs.return_value = 'mock_audio_uri.mp3'

        from datetime import datetime

        from app.models.admin_dashboard_stats import AdminDashboardStats
        from app.models.conversation_scenario import (
            ConversationScenario,
            ConversationScenarioStatus,
        )
        from app.models.session import Session
        from app.models.session_turn import SessionTurn, SpeakerEnum
        from app.models.user_profile import UserProfile

        user_id = uuid4()
        scenario_id = uuid4()
        session_id = uuid4()
        self.session.add(
            UserProfile(
                id=user_id,
                full_name='Test',
                email='a@b.com',
                phone_number='123',
                preferred_language_code=LanguageCode.en,
            )
        )
        self.session.add(AdminDashboardStats())
        # Insert scenario
        scenario = ConversationScenario(
            id=scenario_id,
            user_id=user_id,
            category_id='feedback',
            language_code=LanguageCode.en,
            status=ConversationScenarioStatus.ready,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            persona='',
            situational_facts='',
        )
        self.session.add(scenario)
        session_obj = Session(
            id=session_id,
            scenario_id=scenario_id,
            status=SessionStatus.started,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.session.add(session_obj)
        # Insert at least one turn
        turn = SessionTurn(
            id=uuid4(),
            session_id=session_id,
            speaker=SpeakerEnum.user,
            start_offset_ms=0,
            end_offset_ms=1000,
            text='Hello, Sam!',
            audio_uri='',
            ai_emotion='neutral',
            created_at=datetime.now(),
        )
        self.session.add(turn)
        self.session.commit()

        example_request = FeedbackRequest(
            transcript='Sample transcript...',
            objectives=['Obj1', 'Obj2'],
            persona='**Name**: Someone\n**Training Focus**: Goal',
            situational_facts='Context',
            category='Feedback',
            key_concepts='KC1',
        )
        feedback = generate_and_store_feedback(
            session_id=session_id,
            feedback_request=example_request,
            db_session=self.session,
            scoring_service=mock_scoring_service,
            session_turn_service=mock_session_turn_service,
        )
        # Check feedback score structure
        self.assertEqual(feedback.scores, {'structure': 4, 'empathy': 5, 'focus': 3, 'clarity': 4})
        self.assertEqual(feedback.overall_score, 4.0)
        # Check user_profile statistics
        user = self.session.get(UserProfile, user_id)
        self.assertEqual(user.score_sum, 4.0)
        self.assertEqual(user.total_sessions, 1)
        # Check admin_dashboard_stats statistics
        stats = self.session.exec(select(AdminDashboardStats)).first()
        self.assertEqual(stats.score_sum, 4.0)
        self.assertEqual(stats.total_trainings, 1)
        # Check average score
        self.assertAlmostEqual(user.score_sum / user.total_sessions, 4.0)
        self.assertAlmostEqual(stats.score_sum / stats.total_trainings, 4.0)


if __name__ == '__main__':
    unittest.main()
