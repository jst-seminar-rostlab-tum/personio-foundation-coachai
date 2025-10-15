import unittest
from collections.abc import Generator
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch
from uuid import uuid4

from fastapi import FastAPI
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool.impl import StaticPool
from sqlmodel import Session as DBSession
from sqlmodel import SQLModel, create_engine

from app.data import (
    get_dummy_conversation_categories,
    get_dummy_conversation_scenarios,
    get_dummy_user_data,
)
from app.dependencies import get_db_session
from app.enums import SessionStatus, SpeakerType
from app.models import Session, SessionTurn
from app.services.google_cloud_storage_service import GCSManager
from app.services.session_turn_service import SessionTurnService


def create_mock_gcs_manager() -> GCSManager:
    with (
        patch('app.services.google_cloud_storage_service.settings') as mock_settings,
        patch('app.services.google_cloud_storage_service.storage.Client'),
        patch(
            'app.services.google_cloud_storage_service.service_account.Credentials.from_service_account_info'
        ) as mock_creds,
    ):
        mock_settings.GCP_PROJECT_ID = 'dummy'
        mock_settings.GCP_PRIVATE_KEY_ID = 'dummy'
        mock_settings.GCP_PRIVATE_KEY = (
            '-----BEGIN PRIVATE KEY-----\\ndummy\\n-----END PRIVATE KEY-----\\n'
        )
        mock_settings.GCP_CLIENT_EMAIL = 'dummy@dummy.iam.gserviceaccount.com'
        mock_settings.GCP_CLIENT_ID = 'dummy'
        mock_settings.GCP_BUCKET = 'dummy'
        mock_creds.return_value = MagicMock()

        manager = GCSManager('audio')
        manager.bucket = MagicMock()
        manager.delete_document = MagicMock()
        return manager


class TestSessionService(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.engine = create_engine(
            'sqlite:///:memory:', connect_args={'check_same_thread': False}, poolclass=StaticPool
        )
        SQLModel.metadata.create_all(cls.engine)
        cls.SessionLocal = sessionmaker(bind=cls.engine, class_=DBSession)

        cls.app = FastAPI()

        def override_get_db() -> Generator[DBSession]:
            with cls.SessionLocal() as session:
                yield session

        cls.app.dependency_overrides[get_db_session] = override_get_db

    def setUp(self) -> None:
        SQLModel.metadata.drop_all(self.engine)
        SQLModel.metadata.create_all(self.engine)

        self.db = self.SessionLocal()

        self.users = [u.user_profile for u in get_dummy_user_data()[:2]]
        self.db.add_all(self.users)
        self.db.commit()
        self.user = self.users[0]

        self.categories = get_dummy_conversation_categories()
        self.db.add_all(self.categories)
        self.db.commit()

        self.scenarios = get_dummy_conversation_scenarios(self.users, self.categories)
        self.db.add_all(self.scenarios)
        self.db.commit()

        # Create session
        self.session = Session(
            id=uuid4(),
            scenario_id=self.scenarios[0].id,
            scheduled_at=datetime.now(),
            started_at=datetime.now(),
            ended_at=datetime.now(),
            status=SessionStatus.completed,
        )
        self.db.add(self.session)
        self.db.commit()

        # Create session turns
        self.turn1 = SessionTurn(
            id=uuid4(),
            session_id=self.session.id,
            speaker=SpeakerType.user,
            start_offset_ms=0,
            end_offset_ms=5000,
            text='Hello, how can I help you?',
            audio_uri='dummy/path/to/audio1.wav',
            ai_emotion='neutral',
            created_at=datetime.now(UTC),
        )
        self.turn2 = SessionTurn(
            id=uuid4(),
            session_id=self.session.id,
            speaker=SpeakerType.user,
            start_offset_ms=0,
            end_offset_ms=5000,
            text='Hello, how can I help you?',
            audio_uri='dummy/path/to/audio2.wav',
            ai_emotion='neutral',
            created_at=datetime.now(UTC),
        )
        self.db.add_all([self.turn1, self.turn2])
        self.db.commit()

        # mock GCSManager
        self.mock_gcs = create_mock_gcs_manager()

        patcher = patch(
            'app.services.session_turn_service.get_gcs_audio_manager', return_value=self.mock_gcs
        )
        self.addCleanup(patcher.stop)
        patcher.start()

        self.service = SessionTurnService(self.db)

    def tearDown(self) -> None:
        self.db.rollback()
        self.db.close()

    def test_delete_session_turns_mixed_audio(self) -> None:
        # Verify both session turns exist in the database before deletion
        stmt = select(SessionTurn).where(SessionTurn.id.in_([self.turn1.id, self.turn2.id]))
        remaining_turns = self.db.exec(stmt).all()
        self.assertEqual(len(remaining_turns), 2)

        # Call the service method to delete both session turns
        deleted = self.service.delete_session_turns([self.turn1, self.turn2])

        # Check that the returned list contains the correct audio URIs
        self.assertEqual(deleted, ['dummy/path/to/audio1.wav', 'dummy/path/to/audio2.wav'])

        # Verify that both session turns have been removed from the database
        stmt = select(SessionTurn).where(SessionTurn.id.in_([self.turn1.id, self.turn2.id]))
        remaining_turns = self.db.exec(stmt).all()
        self.assertEqual(len(remaining_turns), 0)


if __name__ == '__main__':
    unittest.main()
