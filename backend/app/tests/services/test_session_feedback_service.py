import unittest
from unittest.mock import MagicMock, patch
from uuid import uuid4

from sqlmodel import Session as DBSession
from sqlmodel import SQLModel, create_engine

from app.models import FeedbackStatusEnum
from app.schemas.session_feedback_schema import (
    ExamplesRequest,
    GoalsAchievedCollection,
    NegativeExample,
    PositiveExample,
    Recommendation,
    RecommendationsCollection,
    RecommendationsRequest,
    SessionExamplesCollection,
)
from app.services.session_feedback_service import (
    generate_and_store_feedback,
    generate_recommendations,
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

    @patch('app.services.session_feedback_service.generate_training_examples')
    @patch('app.services.session_feedback_service.get_achieved_goals')
    @patch('app.services.session_feedback_service.generate_recommendations')
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
            session_id=session_id, example_request=example_request, db_session=self.session
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

    @patch('app.services.session_feedback_service.generate_training_examples')
    @patch('app.services.session_feedback_service.get_achieved_goals')
    @patch('app.services.session_feedback_service.generate_recommendations')
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

    @patch('app.services.session_feedback_service.call_structured_llm')
    def test_generate_recommendation_with_vector_db_prompt_extension(
        self, mock_llm: MagicMock
    ) -> None:
        # Analogically for examples and goals
        transcript = "User: Let's explore what might be causing these delays."
        objectives = ['Understand root causes', 'Collaboratively develop a solution']
        goal = 'Improve team communication'
        key_concepts = '### Active Listening\nAsk open-ended questions.'
        context = 'Project delay review'
        category = 'Project Management'
        other_party = 'Colleague'

        # Set up llm mock and vector db prompt extension
        mock_llm.return_value = RecommendationsCollection(
            recommendations=[
                Recommendation(
                    heading='Practice the STAR method',
                    recommendation='When giving feedback, use the Situation, Task, Action, Result '
                    + 'framework to  provide more concrete examples.',
                )
            ]
        )

        req = RecommendationsRequest(
            category=category,
            context=context,
            other_party=other_party,
            transcript=transcript,
            objectives=objectives,
            goal=goal,
            key_concepts=key_concepts,
        )

        vector_db_prompt_extension_base = (
            'The output you generate should comply with the following HR Guideline excerpts:\n'
        )
        vector_db_prompt_extension_1 = f'{vector_db_prompt_extension_base}Respect\n2. Clarity\n'
        vector_db_prompt_extension_2 = ''

        # Assert for vector_db_prompt_extension_1
        _ = generate_recommendations(req, vector_db_prompt_extension=vector_db_prompt_extension_1)
        assert mock_llm.called
        args, kwargs = mock_llm.call_args
        request_prompt = kwargs['request_prompt']
        assert vector_db_prompt_extension_1 in request_prompt

        # Assert for vector_db_prompt_extension_2
        _ = generate_recommendations(req, vector_db_prompt_extension=vector_db_prompt_extension_2)
        assert mock_llm.called
        args, kwargs = mock_llm.call_args
        request_prompt = kwargs['request_prompt']
        assert vector_db_prompt_extension_base not in request_prompt
        assert len(request_prompt) > 0


if __name__ == '__main__':
    unittest.main()
