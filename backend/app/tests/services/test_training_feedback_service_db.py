import unittest
from unittest.mock import MagicMock, patch
from uuid import uuid4

from sqlmodel import Session, SQLModel, create_engine

from app.models import FeedbackStatusEnum
from app.schemas.training_feedback_schema import (
    ExamplesRequest,
    GoalsAchievedCollection,
    NegativeExample,
    PositiveExample,
    Recommendation,
    RecommendationsCollection,
    TrainingExamplesCollection,
)
from app.services.training_feedback_service import generate_and_store_feedback


class TestTrainingFeedbackService(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.engine = create_engine('sqlite:///:memory:')
        SQLModel.metadata.create_all(cls.engine)
        cls.SessionLocal = Session(cls.engine)

    def setUp(self) -> None:
        self.session = self.SessionLocal

    def tearDown(self) -> None:
        self.session.rollback()

    @patch('app.services.training_feedback_service.generate_training_examples')
    @patch('app.services.training_feedback_service.get_achieved_goals')
    @patch('app.services.training_feedback_service.generate_recommendations')
    def test_generate_and_store_feedback(
        self, mock_recommendations: MagicMock, mock_goals: MagicMock, mock_examples: MagicMock
    ) -> None:
        mock_examples.return_value = TrainingExamplesCollection(
            positive_examples=[
                PositiveExample(
                    heading='Clear Objective Addressed',
                    text='The user successfully summarized the objective.',
                    quote='I want to make sure we both feel heard and find a solution together.',
                    guideline='Collaborative Problem-Solving',
                )
            ],
            negative_examples=[
                NegativeExample(
                    heading='Missed Empathy',
                    text="The user dismissed the other party's concern.",
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
                    text='When giving feedback, use the Situation, Task, '
                    'Action, Result framework to ' + 'provide more concrete examples.',
                ),
                Recommendation(
                    heading='Ask more diagnostic questions',
                    text='Spend more time understanding root causes before moving to solutions. '
                    + 'This builds empathy and leads to more effective outcomes.',
                ),
                Recommendation(
                    heading='Define clear next steps',
                    text='End feedback conversations with agreed-upon action items, timelines, and'
                    + ' follow-up plans.',
                ),
            ]
        )

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
            session_id=session_id, example_request=example_request, db=self.session
        )

        self.assertEqual(feedback.session_id, session_id)
        self.assertEqual(feedback.goals_achieved, 2)

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
            feedback.recommendations[0]['text'],
            'When giving feedback, use the Situation, Task, Action, '
            'Result framework to provide more concrete examples.',
        )
        self.assertEqual(feedback.recommendations[1]['heading'], 'Ask more diagnostic questions')
        self.assertEqual(
            feedback.recommendations[1]['text'],
            'Spend more time understanding root causes before moving to '
            'solutions. This builds empathy and leads to more effective outcomes.',
        )
        self.assertEqual(feedback.recommendations[2]['heading'], 'Define clear next steps')
        self.assertEqual(
            feedback.recommendations[2]['text'],
            'End feedback conversations with agreed-upon action'
            ' items, timelines, and follow-up plans.',
        )
        self.assertEqual(feedback.status, FeedbackStatusEnum.completed)
        self.assertIsNotNone(feedback.created_at)
        self.assertIsNotNone(feedback.updated_at)

    @patch('app.services.training_feedback_service.generate_training_examples')
    @patch('app.services.training_feedback_service.get_achieved_goals')
    @patch('app.services.training_feedback_service.generate_recommendations')
    def test_generate_and_store_feedback_with_errors(
        self, mock_recommendations: MagicMock, mock_goals: MagicMock, mock_examples: MagicMock
    ) -> None:
        mock_examples.side_effect = Exception('Failed to generate examples')

        mock_goals.return_value = GoalsAchievedCollection(goals_achieved=['G1'])
        mock_recommendations.return_value = RecommendationsCollection(
            recommendations=[
                Recommendation(
                    heading='Some heading',
                    text='Some text',
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
            session_id=session_id, example_request=example_request, db=self.session
        )

        self.assertEqual(feedback.status, FeedbackStatusEnum.failed)
        self.assertEqual(feedback.goals_achieved, 1)
        self.assertEqual(len(feedback.example_positive), 0)
        self.assertEqual(len(feedback.recommendations), 1)
        self.assertEqual(feedback.goals_achieved, 1)
        self.assertEqual(len(feedback.example_positive), 0)
        self.assertEqual(len(feedback.recommendations), 1)
        self.assertEqual(feedback.recommendations[0]['heading'], 'Some heading')
        self.assertEqual(feedback.recommendations[0]['text'], 'Some text')

        self.assertIsNotNone(feedback.created_at)
        self.assertIsNotNone(feedback.updated_at)

        self.assertEqual(feedback.overall_score, 0)
        self.assertEqual(feedback.transcript_uri, '')


if __name__ == '__main__':
    unittest.main()
