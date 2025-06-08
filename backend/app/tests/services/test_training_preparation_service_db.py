import unittest
from collections.abc import Generator
from unittest.mock import MagicMock, patch
from uuid import uuid4

from sqlalchemy import create_engine
from sqlmodel import Session as DBSession
from sqlmodel import SQLModel

from app.models.training_preparation import TrainingPreparation, TrainingPreparationStatus
from app.schemas.training_preparation_schema import KeyConcept, TrainingPreparationRequest
from app.services.training_preparation_service import (
    create_pending_preparation,
    generate_training_preparation,
)


class TestTrainingPreparationService(unittest.TestCase):
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
        case_id = uuid4()

        # create a pending preparation
        prep = create_pending_preparation(case_id, self.session)

        # assert the preparation is created with the correct attributes
        self.assertIsNotNone(prep.id)
        self.assertEqual(prep.case_id, case_id)
        self.assertEqual(prep.status, TrainingPreparationStatus.pending)
        self.assertEqual(prep.objectives, [])
        self.assertEqual(prep.key_concepts, [])
        self.assertEqual(prep.prep_checklist, [])

        retrieved = self.session.get(TrainingPreparation, prep.id)
        self.assertIsNotNone(retrieved)

        # assert preparation is still pending
        self.assertEqual(retrieved.status, TrainingPreparationStatus.pending)

    @patch(
        'app.services.training_preparation_service.generate_objectives',
        return_value=['Step 1', 'Step 2'],
    )
    @patch(
        'app.services.training_preparation_service.generate_checklist',
        return_value=['Item A', 'Item B'],
    )
    @patch(
        'app.services.training_preparation_service.generate_key_concept',
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
    def test_generate_training_preparation_completed(
        self, mock_objectives: MagicMock, mock_checklist: MagicMock, mock_key_concept: MagicMock
    ) -> None:
        case_id = uuid4()
        prep = create_pending_preparation(case_id, self.session)

        request = TrainingPreparationRequest(
            category='Feedback',
            goal='Improve communication',
            context='Team review',
            other_party='Product manager',
            num_objectives=2,
            num_checkpoints=2,
        )

        result = generate_training_preparation(prep.id, request, self.fake_session_gen)

        self.assertEqual(result.status, TrainingPreparationStatus.completed)
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

    @patch(
        'app.services.training_preparation_service.generate_key_concept',
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
        'app.services.training_preparation_service.generate_checklist',
        return_value=['Item A', 'Item B'],
    )
    @patch(
        'app.services.training_preparation_service.generate_objectives',
        side_effect=RuntimeError('LLM error'),
    )
    def test_generate_training_preparation_failed(
        self,
        mock_key_concept: MagicMock,
        mock_checklist: MagicMock,
        mock_objectives: MagicMock,
    ) -> None:
        prep = create_pending_preparation(uuid4(), self.session)

        request = TrainingPreparationRequest(
            category='Feedback',
            goal='Improve communication',
            context='Team review',
            other_party='Product manager',
            num_objectives=2,
            num_checkpoints=2,
        )

        result = generate_training_preparation(prep.id, request, self.fake_session_gen)

        # Assert that the preparation status is failed due to LLM error
        self.assertEqual(result.status, TrainingPreparationStatus.failed)
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
