import unittest
from unittest.mock import patch, MagicMock
from sqlmodel import SQLModel, create_engine, Session
from uuid import uuid4
from backend.services.training_feedback_service import generate_and_store_feedback
from backend.models.training_session_feedback import TrainingSessionFeedback, FeedbackStatusEnum
from backend.schemas.training_feedback_schema import ExamplesRequest


class TestTrainingFeedbackService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine("sqlite:///:memory:")
        SQLModel.metadata.create_all(cls.engine)
        cls.SessionLocal = Session(cls.engine)

    def setUp(self):
        self.session = self.SessionLocal

    def tearDown(self):
        self.session.rollback()


    @patch("backend.services.training_feedback_service.generate_training_examples")
    @patch("backend.services.training_feedback_service.get_achieved_goals")
    @patch("backend.services.training_feedback_service.generate_recommendations")
    def test_generate_and_store_feedback(
            self, mock_recommendations, mock_goals, mock_examples
    ):
        # 1. mock responses
        mock_examples.return_value = MagicMock(
            positive_examples=["Good A", "Good B"],
            negative_examples=["Bad A"]
        )
        mock_goals.return_value = MagicMock(goals_achieved=["G1", "G2"])
        mock_recommendations.return_value = MagicMock(
            recommendations=["Tip A", "Tip B"]
        )

        # 2. create example request
        example_request = ExamplesRequest(
            transcript="Sample transcript...",
            objectives=["Obj1", "Obj2"],
            goal="Goal",
            context="Context",
            other_party="Someone",
            category="Feedback",
            key_concepts="KC1"
        )

        session_id = str(uuid4())

        # 3. call the function to generate and store feedback
        feedback = generate_and_store_feedback(
            session_id=session_id,
            example_request=example_request,
            db=self.session
        )

        # 4. assert feedback is not None
        self.assertEqual(feedback.session_id, session_id)
        self.assertEqual(feedback.goals_achieved, 2)
        self.assertEqual(feedback.examples_positive, ["Good A", "Good B"])
        self.assertEqual(feedback.examples_negative, ["Bad A"])
        self.assertEqual(feedback.recommendations, ["Tip A", "Tip B"])
        # self.assertEqual(feedback.status, FeedbackStatusEnum.pending)

        # 5. assert feedback is stored in the database
        retrieved = self.session.get(TrainingSessionFeedback, feedback.id)
        self.assertIsNotNone(retrieved)
