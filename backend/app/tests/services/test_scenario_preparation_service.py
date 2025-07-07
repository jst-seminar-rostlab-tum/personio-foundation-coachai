import unittest
from unittest.mock import MagicMock, patch

from app.schemas.scenario_preparation import (
    ChecklistCreate,
    KeyConcept,
    KeyConceptsCreate,
    KeyConceptsRead,
    ObjectivesCreate,
    StringListRead,
)
from app.services.scenario_preparation.scenario_preparation_service import (
    generate_checklist,
    generate_key_concept,
    generate_objectives,
)


class TestScenarioPreparationService(unittest.TestCase):
    @patch('app.services.scenario_preparation.scenario_preparation_service.call_structured_llm')
    def test_generate_objectives_returns_correct_list(self, mock_llm: MagicMock) -> None:
        items = ['1. Prepare outline', '2. Rehearse responses', '3. Stay calm']
        mock_llm.return_value = StringListRead(items=items)

        req = ObjectivesCreate(
            category='Performance Feedback',
            persona='**Name**: Andrew '
            '**Training Focus**: Giving constructive criticism '
            '**Company Positon**: Junior engineer',
            situational_facts='Quarterly review',
            num_objectives=3,
        )

        result = generate_objectives(req)
        self.assertEqual(len(result), 3)
        self.assertTrue(all(isinstance(item, str) for item in result))
        for i in range(len(result)):
            self.assertEqual(result[i], items[i])

    @patch('app.services.scenario_preparation.scenario_preparation_service.call_structured_llm')
    def test_generate_checklist_returns_correct_list(self, mock_llm: MagicMock) -> None:
        items = ['1. Review past performance', '2. Prepare documents', '3. Set up private room']
        mock_llm.return_value = StringListRead(items=items)

        req = ChecklistCreate(
            category='Performance Review',
            persona='**Name**: Sarah '
            '**Training Focus**: Addressing underperformance '
            '**Company Position**: Backend engineer',
            situational_facts='1:1 review',
            num_checkpoints=3,
        )

        result = generate_checklist(req)
        self.assertEqual(len(result), 3)
        for i in range(len(result)):
            self.assertEqual(result[i], items[i])

    @patch('app.services.scenario_preparation.scenario_preparation_service.call_structured_llm')
    def test_generate_key_concept_parses_json(self, mock_llm: MagicMock) -> None:
        mock_key_concept_response = [
            KeyConcept(
                header='Clear Communication',
                value='Express ideas clearly and listen actively to understand others.',
            ),
            KeyConcept(
                header='Empathy',
                value="Show understanding and concern for the other party's feelings.",
            ),
            KeyConcept(
                header='Effective Questioning',
                value='Ask open-ended questions to encourage dialogue and exploration.',
            ),
        ]

        mock_llm.return_value = KeyConceptsRead(items=mock_key_concept_response)

        req = KeyConceptsCreate(
            category='Feedback',
            persona='**Name**: Jenny'
            '**Training Focus**: Deliver effective criticism'
            '**Company Position**: Project manager',
            situational_facts='Post-project debrief',
        )

        result = generate_key_concept(req)
        self.assertTrue(all(isinstance(x, KeyConcept) for x in result))
        self.assertEqual(result, mock_key_concept_response)

    @patch('app.services.scenario_preparation.scenario_preparation_service.call_structured_llm')
    def test_generate_objectives_with_hr_docs_context(self, mock_llm: MagicMock) -> None:
        # Analogically for checklist and concepts

        # Set up llm mock and vector db prompt extension
        mock_llm.return_value = StringListRead(items=['Objective 1', 'Objective 2'])

        req = ObjectivesCreate(
            category='Feedback',
            persona='**Name**: Glenda'
            '**Training Focus**: Improve team dynamics '
            '**Company Position**: Team lead',
            situational_facts='Team meeting',
            num_objectives=2,
        )

        hr_docs_context_base = (
            'The output you generate should comply with the following HR Guideline excerpts:\n'
        )
        hr_docs_context_1 = f'{hr_docs_context_base}Respect\n2. Clarity\n'
        hr_docs_context_2 = ''

        # Assert for hr_docs_context_1
        _ = generate_objectives(req, hr_docs_context=hr_docs_context_1)
        self.assertTrue(mock_llm.called)
        args, kwargs = mock_llm.call_args
        request_prompt = kwargs['request_prompt']
        self.assertTrue(hr_docs_context_1 in request_prompt)

        # Assert for hr_docs_context_2
        _ = generate_objectives(req, hr_docs_context=hr_docs_context_2)
        self.assertTrue(mock_llm.called)
        args, kwargs = mock_llm.call_args
        request_prompt = kwargs['request_prompt']
        self.assertTrue(hr_docs_context_base not in request_prompt)
        self.assertTrue(len(request_prompt) > 0)
