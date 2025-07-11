import unittest
from unittest.mock import MagicMock, patch

from app.schemas import ConversationScenarioCreate
from app.services.advisor_service import (
    AdvisorService,
    get_mock_advisor_response,
    get_mock_session_feedback,
)


class TestAdvisorService(unittest.TestCase):
    def setUp(self) -> None:
        self.advisor_service = AdvisorService()
        self.llm_mock_response = get_mock_advisor_response()
        self.mock_session_feedback = get_mock_session_feedback()

    @patch('app.services.advisor_service.call_structured_llm')
    def test_score_conversation_calls_llm_and_returns_valid_structure(
        self, mock_call_structured_llm: MagicMock
    ) -> None:
        mock_call_structured_llm.return_value = self.llm_mock_response
        mock_feedback = get_mock_session_feedback()
        conversation_scenario_create, mascot_speech = self.advisor_service.generate_advice(
            mock_feedback
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
