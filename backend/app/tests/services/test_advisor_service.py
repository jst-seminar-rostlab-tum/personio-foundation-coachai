import unittest
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch
from uuid import uuid4

from app.data.populate_static_data import initial_prompt_data
from app.enums import ConversationScenarioStatus, DifficultyLevel, LanguageCode, SessionStatus
from app.models import ConversationCategory, ConversationScenario, Session
from app.schemas import ConversationScenarioCreate
from app.services.advisor_service import (
    AdvisorService,
    get_mock_advisor_response,
    get_mock_session_feedback,
)


def get_previous_session() -> Session:
    scenario_id = uuid4()

    category = ConversationCategory(
        id='performance_reviews',
        name='Performance Reviews',
        initial_prompt=initial_prompt_data.get(
            'performance_reviews', 'Formal performance review meeting.'
        ),
        is_custom=False,
        language_code=LanguageCode.en,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    session = Session(
        id=uuid4(),
        scenario_id=scenario_id,
        scheduled_at=datetime.now(UTC),
        started_at=datetime.now(UTC),
        ended_at=datetime.now(UTC),
        status=SessionStatus.completed,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    scenario = ConversationScenario(
        id=uuid4(),
        user_id=scenario_id,
        category_id='performance_reviews',
        persona_name='angry',
        persona="""
                **Name**: Angry Alex
                **Personality**: Confrontational, defensive, emotionally volatile
                **Behavioral Traits**:
                - Assumes bad intent
                - Easily offended, especially with criticism
                - Challenges authority or decisions
                - Might raise voice
                **Training Focus**:
                - De-escalation techniques
                - Delivering negative feedback calmly
                - Maintaining control in heated situations
                - Validating emotions without losing authority
                **Company Position**: Development Coordinator (5 years experience)""",
        situational_facts="""
                **Missed Deadlines**
                - Quarterly partner-impact report arrived 5 days late despite reminders.
                - Field-visit summary incomplete; colleague had to rewrite it under pressure.

                **Attendance**
                - In the last 2 months, Alex skipped 4 of 8 team check-ins without notice.
                - When present, often keeps camera off and engages minimally.
                
                **Peer Feedback**
                - Two colleagues needed multiple nudges for inputs.
                - One now avoids assigning shared tasks to Alex due to reliability concerns.
                
                **Prior Support**
                - Six weeks ago, the manager set clear expectations and a prioritization plan.
                - Calendar tips and admin help were offered; little improvement seen.

                **Silver Lining**
                - Alex shows real creativity in outreach planning and still has growth potential.
            """,
        difficulty_level=DifficultyLevel.easy,
        status=ConversationScenarioStatus.draft,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    scenario.category = category
    session.scenario = scenario
    return session


class TestAdvisorService(unittest.TestCase):
    def setUp(self) -> None:
        self.advisor_service = AdvisorService()
        self.llm_mock_response = get_mock_advisor_response()
        self.previous_session = get_previous_session()
        self.mock_session_feedback = get_mock_session_feedback()

    @patch('app.services.advisor_service.call_structured_llm')
    def test_generate_advice_no_previous_feedback(
        self, mock_call_structured_llm: MagicMock
    ) -> None:
        mock_call_structured_llm.return_value = self.llm_mock_response
        conversation_scenario_create, mascot_speech = self.advisor_service.generate_advice(
            self.mock_session_feedback
        )
        self.assertIsInstance(conversation_scenario_create, ConversationScenarioCreate)
        self.assertIsInstance(mascot_speech, str)
        self.assertEqual(
            conversation_scenario_create.custom_category_label,
            self.llm_mock_response.custom_category_label,
        )
        self.assertEqual(conversation_scenario_create.persona, self.llm_mock_response.persona)
        self.assertEqual(
            conversation_scenario_create.difficulty_level.name,
            self.llm_mock_response.difficulty_level,
        )
        self.assertEqual(mascot_speech, self.llm_mock_response.mascot_speech)
        request_prompt = mock_call_structured_llm.call_args.kwargs['request_prompt']
        self.assertIn('No previous scenario available', str(request_prompt))

    @patch('app.services.advisor_service.call_structured_llm')
    def test_generate_advice_with_previous_feedback(
        self, mock_call_structured_llm: MagicMock
    ) -> None:
        mock_call_structured_llm.return_value = self.llm_mock_response
        self.mock_session_feedback.session = self.previous_session
        conversation_scenario_create, mascot_speech = self.advisor_service.generate_advice(
            self.mock_session_feedback
        )
        self.assertIsInstance(conversation_scenario_create, ConversationScenarioCreate)
        self.assertIsInstance(mascot_speech, str)
        self.assertEqual(
            conversation_scenario_create.custom_category_label,
            self.llm_mock_response.custom_category_label,
        )
        self.assertEqual(conversation_scenario_create.persona, self.llm_mock_response.persona)
        self.assertEqual(
            conversation_scenario_create.difficulty_level.name,
            self.llm_mock_response.difficulty_level,
        )
        self.assertEqual(mascot_speech, self.llm_mock_response.mascot_speech)
        request_prompt = mock_call_structured_llm.call_args.kwargs['request_prompt']
        self.assertIn(
            self.mock_session_feedback.session.scenario.category.name, str(request_prompt)
        )
        self.assertIn(
            self.mock_session_feedback.session.scenario.difficulty_level.name, str(request_prompt)
        )
