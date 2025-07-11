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


@pytest.fixture
def db() -> Generator[DBSession, None, None]:
    engine = create_engine('sqlite:///:memory:')
    SQLModel.metadata.create_all(engine)
    with DBSession(engine) as session:
        yield session


def test_cleanup_old_session_turns(db: DBSession) -> None:
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

    # Run cleanup
    cleanup_old_session_turns(db)
    db.commit()

    # Assert
    assert db.get(SessionTurn, old_turn.id) is None, (
        'The record from 91 days ago should be deleted.'
    )
    assert db.get(SessionTurn, new_turn.id) is not None, 'The record from today should be kept.'


def test_cleanup_old_session_turns_gcs(db: DBSession) -> None:
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

    # Mock get_gcs_audio_manager
    with patch('app.services.cleanup_service.get_gcs_audio_manager') as mock_gcs_mgr:
        mock_gcs = MagicMock()
        mock_gcs_mgr.return_value = mock_gcs

        cleanup_old_session_turns(db)
        db.commit()

        # Verify that GCS delete_document was called
        mock_gcs.delete_document.assert_called_with(old_audio_uri)
