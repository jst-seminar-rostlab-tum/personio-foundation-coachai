import unittest
from collections.abc import Generator
from unittest.mock import MagicMock, patch
from uuid import uuid4

from sqlalchemy import create_engine
from sqlmodel import Session as DBSession
from sqlmodel import SQLModel

from app.enums.scenario_preparation_status import ScenarioPreparationStatus
from app.models.scenario_preparation import ScenarioPreparation
from app.schemas.scenario_preparation import KeyConcept, ScenarioPreparationCreate
from app.services.scenario_preparation.scenario_preparation_service import (
    create_pending_preparation,
    generate_scenario_preparation,
)


class TestScenarioPreparationService(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.engine = create_engine('sqlite:///:memory:')
        print('creating in-memory SQLite database for testing')
        SQLModel.metadata.create_all(cls.engine)
        print('Database schema created')
        cls.SessionLocal = DBSession(cls.engine)

    def setUp(self) -> None:
        self.session = self.SessionLocal

    def tearDown(self) -> None:
        self.session.rollback()

    def fake_session_gen(self) -> Generator[DBSession, None, None]:
        yield self.session

    def test_create_pending_preparation(self) -> None:
        scenario_id = uuid4()

        # create a pending preparation
        prep = create_pending_preparation(scenario_id, self.session)

        # assert the preparation is created with the correct attributes
        self.assertIsNotNone(prep.id)
        self.assertEqual(prep.scenario_id, scenario_id)
        self.assertEqual(prep.status, ScenarioPreparationStatus.pending)
        self.assertEqual(prep.objectives, [])
        self.assertEqual(prep.key_concepts, [])
        self.assertEqual(prep.prep_checklist, [])

        retrieved = self.session.get(ScenarioPreparation, prep.id)
        self.assertIsNotNone(retrieved)

        # assert preparation is still pending
        if retrieved is None:
            self.fail('Preparation not found in the database after creation')
        self.assertEqual(retrieved.status, ScenarioPreparationStatus.pending)

    @patch(
        'app.services.scenario_preparation.scenario_preparation_service.generate_objectives',
        return_value=['Step 1', 'Step 2'],
    )
    @patch(
        'app.services.scenario_preparation.scenario_preparation_service.generate_checklist',
        return_value=['Item A', 'Item B'],
    )
    @patch(
        'app.services.scenario_preparation.scenario_preparation_service.generate_key_concept',
        return_value=[
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
        ],
    )
    def test_generate_scenario_preparation_completed(
        self, mock_objectives: MagicMock, mock_checklist: MagicMock, mock_key_concept: MagicMock
    ) -> None:
        scenario_id = uuid4()
        prep = create_pending_preparation(scenario_id, self.session)

        new_preparation = ScenarioPreparationCreate(
            category='Feedback',
            persona='**Name**: Jenny'
            '**Training Focus**: Improve communication'
            '**Company Position**: Product manager',
            situational_facts='Team review',
            num_objectives=2,
            num_checkpoints=2,
        )

        result = generate_scenario_preparation(prep.id, new_preparation, self.fake_session_gen)

        self.assertEqual(result.status, ScenarioPreparationStatus.completed)
        self.assertEqual(result.objectives, ['Step 1', 'Step 2'])
        self.assertEqual(result.prep_checklist, ['Item A', 'Item B'])
        self.assertEqual(
            result.key_concepts,
            [
                {
                    'header': 'Clear Communication',
                    'value': 'Express ideas clearly and listen actively to understand others.',
                },
                {
                    'header': 'Empathy',
                    'value': "Show understanding and concern for the other party's feelings.",
                },
                {
                    'header': 'Effective Questioning',
                    'value': 'Ask open-ended questions to encourage dialogue and exploration.',
                },
            ],
        )
        self.assertIsInstance(result.document_names, list)

    @patch(
        'app.services.scenario_preparation.scenario_preparation_service.generate_key_concept',
        return_value=[
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
        ],
    )
    @patch(
        'app.services.scenario_preparation.scenario_preparation_service.generate_checklist',
        return_value=['Item A', 'Item B'],
    )
    @patch(
        'app.services.scenario_preparation.scenario_preparation_service.generate_objectives',
        side_effect=RuntimeError('LLM error'),
    )
    def test_generate_scenario_preparation_failed(
        self,
        mock_key_concept: MagicMock,
        mock_checklist: MagicMock,
        mock_objectives: MagicMock,
    ) -> None:
        prep = create_pending_preparation(uuid4(), self.session)

        new_preparation = ScenarioPreparationCreate(
            category='Feedback',
            persona='**Name**: Jenny'
            '**Training Focus**: Improve communication'
            '**Company Position**: Product manager',
            situational_facts='Team review',
            num_objectives=2,
            num_checkpoints=2,
        )

        result = generate_scenario_preparation(prep.id, new_preparation, self.fake_session_gen)

        # Assert that the preparation status is failed due to LLM error
        self.assertEqual(result.status, ScenarioPreparationStatus.failed)
        self.assertEqual(result.prep_checklist, ['Item A', 'Item B'])
        self.assertEqual(
            result.key_concepts,
            [
                {
                    'header': 'Clear Communication',
                    'value': 'Express ideas clearly and listen actively to understand others.',
                },
                {
                    'header': 'Empathy',
                    'value': "Show understanding and concern for the other party's feelings.",
                },
                {
                    'header': 'Effective Questioning',
                    'value': 'Ask open-ended questions to encourage dialogue and exploration.',
                },
            ],
        )
        self.assertEqual(result.objectives, [])


if __name__ == '__main__':
    unittest.main()
