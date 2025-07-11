from collections.abc import Generator
from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from sqlmodel import Session as DBSession
from sqlmodel import SQLModel, create_engine

from app.models.session import Session
from app.models.session_turn import SessionTurn, SpeakerEnum
from app.services.cleanup_service import cleanup_old_session_turns
from app.services.google_cloud_storage_service import GCSManager


@pytest.fixture
def gcs_manager() -> GCSManager:
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
        return manager


@pytest.fixture
def db() -> Generator[DBSession, None, None]:
    engine = create_engine('sqlite:///:memory:')
    SQLModel.metadata.create_all(engine)
    with DBSession(engine) as session:
        yield session


def test_cleanup_old_session_turns(db: DBSession, gcs_manager: GCSManager) -> None:
    # Create a session
    session_id = uuid4()
    db.add(Session(id=session_id, scenario_id=uuid4()))
    db.commit()

    # Insert a record from 91 days ago (should be deleted)
    old_turn = SessionTurn(
        session_id=session_id,
        speaker=SpeakerEnum.user,
        start_offset_ms=0,
        end_offset_ms=1000,
        text='old',
        audio_uri='old_uri.mp3',
        created_at=datetime.now(UTC) - timedelta(days=91),
    )
    # Insert a record from today (should be kept)
    new_turn = SessionTurn(
        session_id=session_id,
        speaker=SpeakerEnum.user,
        start_offset_ms=0,
        end_offset_ms=1000,
        text='new',
        audio_uri='new_uri.mp3',
        created_at=datetime.now(UTC),
    )
    db.add(old_turn)
    db.add(new_turn)
    db.commit()

    old_turn_id = old_turn.id
    new_turn_id = new_turn.id

    with patch('app.services.cleanup_service.get_gcs_audio_manager', return_value=gcs_manager):
        cleanup_old_session_turns(db)
        db.commit()

    assert db.get(SessionTurn, old_turn_id) is None
    assert db.get(SessionTurn, new_turn_id) is not None


def test_cleanup_old_session_turns_gcs(db: DBSession, gcs_manager: GCSManager) -> None:
    session_id = uuid4()
    db.add(Session(id=session_id, scenario_id=uuid4()))
    db.commit()

    old_audio_uri = 'old_uri.mp3'
    old_turn = SessionTurn(
        session_id=session_id,
        speaker=SpeakerEnum.user,
        start_offset_ms=0,
        end_offset_ms=1000,
        text='old',
        audio_uri=old_audio_uri,
        created_at=datetime.now(UTC) - timedelta(days=91),
    )
    db.add(old_turn)
    db.commit()

    with (
        patch('app.services.cleanup_service.get_gcs_audio_manager', return_value=gcs_manager),
        patch.object(gcs_manager, 'delete_document') as mock_delete,
    ):
        cleanup_old_session_turns(db)
        db.commit()
        mock_delete.assert_called_with(old_audio_uri)
