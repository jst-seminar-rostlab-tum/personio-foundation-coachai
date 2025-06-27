import unittest
from unittest.mock import MagicMock, patch
from uuid import uuid4

from sqlmodel import Session as DBSession
from sqlmodel import SQLModel, create_engine, select

from app.models import FeedbackStatusEnum
from app.schemas.session_feedback import (
    ExamplesRequest,
    GoalsAchievedCollection,
    NegativeExample,
    PositiveExample,
    Recommendation,
    RecommendationsCollection,
    SessionExamplesCollection,
)
from app.services.session_feedback.session_feedback_service import generate_and_store_feedback


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

    @patch('app.services.session_feedback.session_feedback_service.generate_training_examples')
    @patch('app.services.session_feedback.session_feedback_service.get_achieved_goals')
    @patch('app.services.session_feedback.session_feedback_service.generate_recommendations')
    def test_generate_and_store_feedback(
        self, mock_recommendations: MagicMock, mock_goals: MagicMock, mock_examples: MagicMock
    ) -> None:
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

        example_request = ExamplesRequest(
            transcript='Sample transcript...',
            objectives=['Obj1', 'Obj2'],
            goal='Goal',
            context='Context',
            other_party='Someone',
            category='Feedback',
            key_concepts='KC1',
        )

        session_id = uuid4()

        feedback = generate_and_store_feedback(
            session_id=session_id,
            example_request=example_request,
            db_session=self.session,
            scoring_service=mock_scoring_service,
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

    @patch('app.services.session_feedback.session_feedback_service.generate_training_examples')
    @patch('app.services.session_feedback.session_feedback_service.get_achieved_goals')
    @patch('app.services.session_feedback.session_feedback_service.generate_recommendations')
    def test_generate_and_store_feedback_with_errors(
        self, mock_recommendations: MagicMock, mock_goals: MagicMock, mock_examples: MagicMock
    ) -> None:
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

        example_request = ExamplesRequest(
            transcript='Error case transcript...',
            objectives=['ObjX'],
            goal='Goal',
            context='Context',
            other_party='Other',
            category='Category',
            key_concepts='KeyConcept',
        )

        session_id = uuid4()

        feedback = generate_and_store_feedback(
            session_id=session_id, example_request=example_request, db_session=self.session
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

    @patch('app.services.session_feedback.session_feedback_service.generate_training_examples')
    @patch('app.services.session_feedback.session_feedback_service.get_achieved_goals')
    @patch('app.services.session_feedback.session_feedback_service.generate_recommendations')
    def test_scoring_and_stats_update(
        self, mock_recommendations: MagicMock, mock_goals: MagicMock, mock_examples: MagicMock
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

        # 创建user_profile和admin_dashboard_stats
        from app.models.admin_dashboard_stats import AdminDashboardStats
        from app.models.user_profile import UserProfile

        user_id = uuid4()
        self.session.add(
            UserProfile(
                id=user_id,
                full_name='Test',
                email='a@b.com',
                phone_number='123',
                preferred_language_code='en',
            )
        )
        self.session.add(AdminDashboardStats())
        self.session.commit()

        example_request = ExamplesRequest(
            transcript='Sample transcript...',
            objectives=['Obj1', 'Obj2'],
            goal='Goal',
            context='Context',
            other_party='Someone',
            category='Feedback',
            key_concepts='KC1',
        )
        feedback = generate_and_store_feedback(
            session_id=user_id,
            example_request=example_request,
            db_session=self.session,
            scoring_service=mock_scoring_service,
        )
        # 检查feedback分数结构
        self.assertEqual(feedback.scores, {'structure': 4, 'empathy': 5, 'focus': 3, 'clarity': 4})
        self.assertEqual(feedback.overall_score, 4.0)
        # 检查user_profile统计
        user = self.session.get(UserProfile, user_id)
        self.assertEqual(user.score_sum, 4.0)
        self.assertEqual(user.total_sessions, 1)
        # 检查admin_dashboard_stats统计
        stats = self.session.exec(select(AdminDashboardStats)).first()
        self.assertEqual(stats.score_sum, 4.0)
        self.assertEqual(stats.total_trainings, 1)
        # 平均分计算
        self.assertAlmostEqual(user.score_sum / user.total_sessions, 4.0)
        self.assertAlmostEqual(stats.score_sum / stats.total_trainings, 4.0)


if __name__ == '__main__':
    unittest.main()
