import unittest
from collections.abc import Generator
from datetime import datetime
from typing import Any
from unittest.mock import MagicMock, patch
from uuid import uuid4

from sqlmodel import Session as DBSession
from sqlmodel import SQLModel, create_engine, select

from app.enums import FeedbackStatus
from app.enums.language import LanguageCode
from app.enums.speaker import SpeakerType
from app.models.conversation_scenario import ConversationScenarioStatus
from app.models.user_profile import UserProfile
from app.schemas.conversation_scenario import (
    ConversationScenario,
    ConversationScenarioRead,
)
from app.schemas.session_feedback import (
    FeedbackCreate,
    GoalsAchievedCreate,
    GoalsAchievedRead,
    NegativeExample,
    PositiveExample,
    Recommendation,
    RecommendationsRead,
    SessionExamplesRead,
)
from app.schemas.session_turn import SessionTurnRead, SessionTurnStitchAudioSuccess
from app.services.session_feedback.session_feedback_llm import generate_recommendations
from app.services.session_feedback.session_feedback_service import (
    generate_and_store_feedback,
    generate_feedback_components,
)


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
        )

    def tearDown(self) -> None:
        self.session.rollback()

    def _mock_conversation_data(self) -> ConversationScenarioRead:
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
            )
        )
        self.session.commit()
        scenario = ConversationScenario(
            id=uuid4(),
            user_id=user_id,
            category_id='feedback',
            custom_category_label=None,
            persona_name='Test Persona',
            persona='',
            situational_facts='',
            language_code=LanguageCode.en,
            status=ConversationScenarioStatus.ready,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        transcript = [
            SessionTurnRead(
                id=uuid4(),
                speaker=SpeakerType.user,
                full_audio_start_offset_ms=0,
                text='Hello, Sam!',
                ai_emotion='neutral',
                created_at=datetime.now(),
            )
        ]
        return ConversationScenarioRead(scenario=scenario, transcript=transcript)

    @patch('app.services.session_feedback.session_feedback_service.get_hr_docs_context')
    @patch('app.services.session_feedback.session_feedback_service.get_conversation_data')
    @patch('app.services.session_feedback.session_feedback_service.get_gcs_audio_manager')
    @patch('app.services.session_feedback.session_feedback_llm.generate_training_examples')
    @patch('app.services.session_feedback.session_feedback_llm.get_achieved_goals')
    @patch('app.services.session_feedback.session_feedback_llm.generate_recommendations')
    def test_generate_and_store_feedback(
        self,
        mock_recommendations: MagicMock,
        mock_goals: MagicMock,
        mock_examples: MagicMock,
        mock_get_gcs_audio_manager: MagicMock,
        mock_get_conversation_data: MagicMock,
        mock_get_hr_docs_context: MagicMock,
    ) -> None:
        mock_gcs = MagicMock()
        mock_gcs.generate_signed_url.return_value = 'https://mock.audio/signed_url.mp3'
        mock_get_gcs_audio_manager.return_value = mock_gcs

        mock_get_conversation_data.return_value = self._mock_conversation_data()
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

        mock_get_hr_docs_context.return_value = ('Some HR context', ['Doc1', 'Doc2'], [{}, {}])

        # Inject mock scoring_service
        class MockScore:
            def __init__(self, metric: str, score: float) -> None:
                self.metric = metric
                self.score = score

        class MockScoringRead:
            class Scoring:
                def __init__(self) -> None:
                    self.scores = [
                        MockScore('structure', 4),
                        MockScore('empathy', 5),
                        MockScore('focus', 3),
                        MockScore('clarity', 4),
                    ]
                    self.overall_score = 16.0

            def __init__(self) -> None:
                self.scoring = self.Scoring()

        mock_scoring_service = MagicMock()
        mock_scoring_service.safe_score_conversation.return_value = MockScoringRead()

        mock_session_turn_service = MagicMock()
        mock_session_turn_service.stitch_mp3s_from_gcs.return_value = SessionTurnStitchAudioSuccess(
            output_filename='mock_audio_uri.mp3',
            audio_duration_s=120,
        )

        example_request = FeedbackCreate(
            transcript='Sample transcript...',
            objectives=['Obj1', 'Obj2'],
            persona='**Name**: Someone\n**Training Focus**: Goal\n'
            '**Company Position**: Team Member',
            situational_facts='Context',
            category='Feedback',
            key_concepts='KC1',
        )

        session_id = uuid4()

        def mock_session_generator_func() -> Generator[Any]:
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

        self.assertIsInstance(feedback.documents, list)
        self.assertEqual(feedback.documents, [{}, {}])

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

    @patch('app.services.session_feedback.session_feedback_service.get_conversation_data')
    @patch('app.services.session_feedback.session_feedback_llm.generate_training_examples')
    @patch('app.services.session_feedback.session_feedback_service.get_gcs_audio_manager')
    @patch('app.services.session_feedback.session_feedback_llm.get_achieved_goals')
    @patch('app.services.session_feedback.session_feedback_llm.generate_recommendations')
    def test_generate_and_store_feedback_with_errors(
        self,
        mock_recommendations: MagicMock,
        mock_goals: MagicMock,
        mock_get_gcs_audio_manager: MagicMock,
        mock_examples: MagicMock,
        mock_get_conversation_data: MagicMock,
    ) -> None:
        mock_gcs = MagicMock()
        mock_gcs.generate_signed_url.return_value = 'https://mock.audio/signed_url.mp3'
        mock_get_gcs_audio_manager.return_value = mock_gcs

        mock_get_conversation_data.return_value = self._mock_conversation_data()
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

        example_request = FeedbackCreate(
            transcript='Error case transcript...',
            objectives=['ObjX'],
            persona='**Name**: Example User\n**Training Focus**: Goal\n'
            '**Company Position**: Example Position',
            situational_facts='Context',
            category='Category',
            key_concepts='KeyConcept',
        )

        session_id = uuid4()

        class MockScoringRead:
            class Scoring:
                def __init__(self) -> None:
                    self.scores = []
                    self.overall_score = 1.0

            def __init__(self) -> None:
                self.scoring = self.Scoring()

        mock_scoring_service = MagicMock()
        mock_scoring_service.safe_score_conversation.return_value = MockScoringRead()

        mock_session_turn_service = MagicMock()
        mock_session_turn_service.stitch_mp3s_from_gcs.return_value = SessionTurnStitchAudioSuccess(
            output_filename='mock_audio_uri.mp3',
            audio_duration_s=120,
        )

        def mock_session_generator_func() -> Generator[Any]:
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

        self.assertEqual(feedback.overall_score, 1)

    @patch('app.services.session_feedback.session_feedback_llm.call_structured_llm')
    def test_generate_recommendation_with_hr_docs_context(self, mock_llm: MagicMock) -> None:
        # Analogically for examples and goals
        transcript = "User: Let's explore what might be causing these delays."
        objectives = ['Understand root causes', 'Collaboratively develop a solution']
        key_concepts = '### Active Listening\nAsk open-ended questions.'
        category = 'Project Management'

        # Set up llm mock and vector db prompt extension
        mock_llm.return_value = RecommendationsRead(
            recommendations=[
                Recommendation(
                    heading='Practice the STAR method',
                    recommendation='When giving feedback, use the Situation, Task, Action, Result '
                    + 'framework to  provide more concrete examples.',
                )
            ]
        )

        req = FeedbackCreate(
            category=category,
            transcript=transcript,
            objectives=objectives,
            persona='**Name**: John\n**Training Focus**: Improve team communication\n'
            '**Company Position**: Colleague',
            situational_facts='Project delay review',
            key_concepts=key_concepts,
        )

        hr_docs_context_base = (
            'The output you generate should comply with the following HR Guideline excerpts:\n'
        )
        hr_docs_context_1 = f'{hr_docs_context_base}Respect\n2. Clarity\n'
        hr_docs_context_2 = ''

        # Assert for hr_docs_context_1
        _ = generate_recommendations(req, hr_docs_context=hr_docs_context_1)
        self.assertTrue(mock_llm.called)
        args, kwargs = mock_llm.call_args
        request_prompt = kwargs['request_prompt']
        self.assertTrue(hr_docs_context_1 in request_prompt)

        # Assert for hr_docs_context_2
        _ = generate_recommendations(req, hr_docs_context=hr_docs_context_2)
        self.assertTrue(mock_llm.called)
        args, kwargs = mock_llm.call_args
        request_prompt = kwargs['request_prompt']
        self.assertTrue(hr_docs_context_base not in request_prompt)
        self.assertTrue(len(request_prompt) > 0)

    @patch('app.services.session_feedback.session_feedback_service.get_conversation_data')
    @patch('app.services.session_feedback.session_feedback_llm.generate_training_examples')
    @patch('app.services.session_feedback.session_feedback_llm.get_achieved_goals')
    @patch('app.services.session_feedback.session_feedback_llm.generate_recommendations')
    def test_scoring_and_stats_update(
        self,
        mock_recommendations: MagicMock,
        mock_goals: MagicMock,
        mock_examples: MagicMock,
        mock_get_conversation_data: MagicMock,
    ) -> None:
        mock_examples.return_value = SessionExamplesRead(positive_examples=[], negative_examples=[])
        mock_goals.return_value = GoalsAchievedRead(goals_achieved=[])
        mock_recommendations.return_value = RecommendationsRead(recommendations=[])

        class MockScore:
            def __init__(self, metric: str, score: float) -> None:
                self.metric = metric
                self.score = score

        class MockScoringRead:
            class Scoring:
                def __init__(self) -> None:
                    self.scores = [
                        MockScore('structure', 4),
                        MockScore('empathy', 5),
                        MockScore('focus', 3),
                        MockScore('clarity', 4),
                    ]
                    self.overall_score = 16.0

            def __init__(self) -> None:
                self.scoring = self.Scoring()

        mock_scoring_service = MagicMock()
        mock_scoring_service.safe_score_conversation.return_value = MockScoringRead()

        mock_session_turn_service = MagicMock()
        mock_session_turn_service.stitch_mp3s_from_gcs.return_value = SessionTurnStitchAudioSuccess(
            output_filename='mock_audio_uri.mp3',
            audio_duration_s=120,
        )
        session_id = uuid4()
        mock_get_conversation_data.return_value = self._mock_conversation_data()

        example_request = FeedbackCreate(
            transcript='Sample transcript...',
            objectives=['Obj1', 'Obj2'],
            persona='**Name**: Someone\n**Training Focus**: Goal',
            situational_facts='Context',
            category='Feedback',
            key_concepts='KC1',
        )

        def mock_session_generator_func() -> Generator[Any]:
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
        self.assertDictEqual(
            feedback.scores, {'structure': 4, 'empathy': 5, 'focus': 3, 'clarity': 4}
        )
        self.assertEqual(feedback.overall_score, 16.0)

    def test_generate_training_examples_with_audio(self) -> None:
        from app.schemas.session_feedback import FeedbackCreate, SessionExamplesRead
        from app.services.session_feedback import session_feedback_llm

        dummy_audio_uri = 'https://dummy-audio-uri'
        dummy_examples = SessionExamplesRead(positive_examples=[], negative_examples=[])
        req = FeedbackCreate(
            transcript='User: Hello',
            objectives=['Obj1'],
            persona='P',
            situational_facts='S',
            category='C',
            key_concepts='K',
        )
        with patch.object(
            session_feedback_llm, 'call_structured_llm', return_value=dummy_examples
        ) as mock_audio:
            result = session_feedback_llm.generate_training_examples(
                req, hr_docs_context='', audio_uri=dummy_audio_uri
            )
            mock_audio.assert_called_once()
            self.assertEqual(mock_audio.call_args.kwargs['audio_uri'], dummy_audio_uri)
            self.assertTrue(hasattr(result, 'positive_examples'))
            self.assertTrue(hasattr(result, 'negative_examples'))

    def test_generate_recommendations_with_audio(self) -> None:
        from app.schemas.session_feedback import FeedbackCreate, Recommendation, RecommendationsRead
        from app.services.session_feedback import session_feedback_llm

        dummy_audio_uri = 'https://dummy-audio-uri'
        dummy_recommendations = RecommendationsRead(
            recommendations=[Recommendation(heading='h', recommendation='r')]
        )
        req = FeedbackCreate(
            transcript='User: Hello',
            objectives=['Obj1'],
            persona='P',
            situational_facts='S',
            category='C',
            key_concepts='K',
        )
        with patch.object(
            session_feedback_llm, 'call_structured_llm', return_value=dummy_recommendations
        ) as mock_audio:
            result = session_feedback_llm.generate_recommendations(
                req, hr_docs_context='', audio_uri=dummy_audio_uri
            )
            mock_audio.assert_called_once()
            self.assertEqual(mock_audio.call_args.kwargs['audio_uri'], dummy_audio_uri)
            self.assertTrue(hasattr(result, 'recommendations'))
            self.assertEqual(result.recommendations[0].heading, 'h')
            self.assertEqual(result.recommendations[0].recommendation, 'r')

    def test_get_achieved_goals_with_audio(self) -> None:
        from app.schemas.session_feedback import GoalsAchievedRead
        from app.services.session_feedback import session_feedback_llm

        dummy_audio_uri = 'https://dummy-audio-uri'
        dummy_goals = GoalsAchievedRead(goals_achieved=['G1', 'G2'])
        req = GoalsAchievedCreate(
            transcript='User: Hello',
            objectives=['Obj1'],
            language_code=LanguageCode.en,
        )
        with patch.object(
            session_feedback_llm, 'call_structured_llm', return_value=dummy_goals
        ) as mock_audio:
            result = session_feedback_llm.get_achieved_goals(
                req, hr_docs_context='', audio_uri=dummy_audio_uri
            )
            mock_audio.assert_called_once()
            self.assertEqual(mock_audio.call_args.kwargs['audio_uri'], dummy_audio_uri)
            self.assertTrue(hasattr(result, 'goals_achieved'))
            self.assertEqual(result.goals_achieved, ['G1', 'G2'])

    @patch('app.services.session_feedback.session_feedback_service.get_conversation_data')
    @patch('app.services.session_feedback.session_feedback_llm.generate_training_examples')
    @patch('app.services.session_feedback.session_feedback_llm.get_achieved_goals')
    @patch('app.services.session_feedback.session_feedback_llm.generate_recommendations')
    def test_generate_feedback_no_audio_url_when_store_audio_fails(
        self,
        mock_recommendations: MagicMock,
        mock_goals: MagicMock,
        mock_examples: MagicMock,
        mock_get_conversation_data: MagicMock,
    ) -> None:
        mock_get_conversation_data.return_value = self._mock_conversation_data()
        mock_examples.return_value = SessionExamplesRead(positive_examples=[], negative_examples=[])
        mock_goals.return_value = GoalsAchievedRead(goals_achieved=['G1'])
        mock_recommendations.return_value = RecommendationsRead(
            recommendations=[Recommendation(heading='h', recommendation='r')]
        )

        # Setup mock scoring
        class MockScoringRead:
            class Scoring:
                def __init__(self) -> None:
                    self.scores = []
                    self.overall_score = 10.0

            def __init__(self) -> None:
                self.scoring = self.Scoring()

        mock_scoring_service = MagicMock()
        mock_scoring_service.safe_score_conversation.return_value = MockScoringRead()

        # simulate session_turn_service successfully stitching audio
        mock_session_turn_service = MagicMock()
        mock_session_turn_service.stitch_mp3s_from_gcs.return_value = SessionTurnStitchAudioSuccess(
            output_filename='mock_audio_uri.mp3',
            audio_duration_s=100,
        )

        # simulate generating signed URL for audio failure
        with patch(
            'app.services.session_feedback.session_feedback_service.get_gcs_audio_manager'
        ) as mock_gcs_manager:
            mock_gcs = MagicMock()
            mock_gcs.generate_signed_url.side_effect = Exception(
                'Signed URL should not be generated'
            )
            mock_gcs_manager.return_value = mock_gcs

            conversation = self._mock_conversation_data()

            feedback = generate_feedback_components(
                feedback_request=FeedbackCreate(
                    transcript='Mock transcript',
                    objectives=['O1'],
                    persona='P',
                    situational_facts='S',
                    category='Feedback',
                    key_concepts='K',
                ),
                goals_request=GoalsAchievedCreate(
                    transcript='Mock transcript',
                    objectives=['O1'],
                    language_code=LanguageCode.en,
                ),
                hr_docs_context='',
                documents=[{}, {}],
                conversation=conversation,
                scoring_service=mock_scoring_service,
                session_turn_service=mock_session_turn_service,
                session_id=uuid4(),
            )

            self.assertTrue(feedback.audio_url is None)
            self.assertEqual(feedback.goals, GoalsAchievedRead(goals_achieved=['G1']))

            self.assertEqual(feedback.documents, [{}, {}])
            self.assertEqual(feedback.full_audio_filename, 'mock_audio_uri.mp3')
            self.assertEqual(feedback.session_length_s, 100)

            self.assertEqual(feedback.overall_score, 10.0)
            self.assertEqual(feedback.has_error, False)


if __name__ == '__main__':
    unittest.main()
