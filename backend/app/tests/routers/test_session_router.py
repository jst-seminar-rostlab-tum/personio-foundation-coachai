import unittest
from collections.abc import Generator
from datetime import datetime
from unittest.mock import MagicMock, patch
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool.impl import StaticPool
from sqlmodel import Session as DBSession
from sqlmodel import SQLModel, create_engine

from app.data.dummy_data import (
    get_dummy_conversation_categories,
    get_dummy_conversation_scenarios,
    get_dummy_session_feedback,
)
from app.dependencies import get_db_session, require_user
from app.main import app
from app.models import Review, Session, SessionStatus, UserProfile
from app.models.session_turn import SpeakerEnum
from app.models.user_profile import AccountRole
from app.schemas.session_turn import SessionTurnRead


class FakeGCS:
    def __init__(self) -> None:
        pass

    def generate_signed_url(self, filename: str) -> str:
        return f'https://example.com/{filename}'


class TestSessionRoute(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # Create an in-memory SQLite database for testing
        cls.engine = create_engine(
            'sqlite:///:memory:', connect_args={'check_same_thread': False}, poolclass=StaticPool
        )
        SQLModel.metadata.create_all(cls.engine)
        cls.SessionLocal = sessionmaker(bind=cls.engine, class_=DBSession)

    def setUp(self) -> None:
        # patch GCSManager so it always returns your FakeGCS…
        self.gcs_patcher = patch(
            'app.services.session_service.GCSManager',  # <- the import path your code uses
            return_value=FakeGCS(),
        )
        self.mock_gcs_cls = self.gcs_patcher.start()

        self.db = self.SessionLocal()

        def override_get_db() -> Generator[Session, None, None]:
            yield self.db

        # Override the get_db_session dependency
        app.dependency_overrides[get_db_session] = override_get_db

        # mock require_user
        self.test_user = UserProfile(
            id=uuid4(),
            full_name='Test User',
            email='test@example.com',
            phone_number='1234567890',
            account_role=AccountRole.user,
        )
        self.db.add(self.test_user)
        self.db.commit()

        app.dependency_overrides[require_user] = lambda: self.test_user

        self.client = TestClient(app)

        # Populate dummy data
        conversation_categories = get_dummy_conversation_categories()
        self.db.add_all(conversation_categories)
        self.db.commit()

        # Create dummy conversation scenarios
        conversation_scenarios = get_dummy_conversation_scenarios(
            [self.test_user, self.test_user], conversation_categories
        )

        self.db.add_all(conversation_scenarios)
        self.db.commit()

        # Create a test session
        self.test_session = Session(
            id=uuid4(),
            scenario_id=conversation_scenarios[0].id,
            scheduled_at=datetime.now(),
            started_at=datetime.now(),
            ended_at=datetime.now(),
            status=SessionStatus.completed,
        )
        self.db.add(self.test_session)
        self.db.commit()

        fake_turn_svc = MagicMock()
        fake_turn_svc.get_session_turns.return_value = [
            SessionTurnRead(
                id=uuid4(),
                session_id=self.test_session.id,
                speaker=SpeakerEnum.user,
                full_audio_start_offset_ms=0,
                text='hello',
                ai_emotion='neutral',
                created_at=datetime.now(),
            )
        ]
        self.turn_patcher = patch(
            'app.services.session_service.SessionTurnService', return_value=fake_turn_svc
        )
        self.turn_patcher.start()

    def tearDown(self) -> None:
        self.turn_patcher.stop()
        self.gcs_patcher.stop()
        self.db.rollback()
        self.db.close()

    def test_get_session_by_id(self) -> None:
        response = self.client.get(f'/session/{self.test_session.id}')

        # Assert without feedback yet
        self.assertEqual(response.status_code, 202)

        self.assertEqual(response.json()['detail'], 'Session feedback in progress.')
        dummy_feedback = get_dummy_session_feedback([self.test_session] * 8)
        self.db.add_all(dummy_feedback)
        self.db.commit()

        response = self.client.get(f'/session/{self.test_session.id}')
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data['scenarioId'], str(self.test_session.scenario_id))
        self.assertEqual(data['id'], str(self.test_session.id))
        self.assertEqual(data['status'], 'completed')
        self.assertEqual(data['scheduledAt'], self.test_session.scheduled_at.isoformat())
        self.assertEqual(data['startedAt'], self.test_session.started_at.isoformat())
        self.assertEqual(data['endedAt'], self.test_session.ended_at.isoformat())
        self.assertEqual(data['createdAt'], self.test_session.created_at.isoformat())
        self.assertEqual(data['updatedAt'], self.test_session.updated_at.isoformat())
        self.assertEqual(data['allowAdminAccess'], False)
        self.assertEqual(data['hasReviewed'], False)

        # Add Review
        review = Review(
            id=uuid4(),
            user_id=self.test_user.id,
            session_id=self.test_session.id,  # Link to the first session
            rating=5,
            comment='Excellent service!',
        )
        self.db.add(review)
        self.db.commit()

        response = self.client.get(f'/session/{self.test_session.id}')
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['scenarioId'], str(self.test_session.scenario_id))
        self.assertEqual(data['id'], str(self.test_session.id))
        self.assertEqual(data['status'], 'completed')
        self.assertEqual(data['scheduledAt'], self.test_session.scheduled_at.isoformat())
        self.assertEqual(data['startedAt'], self.test_session.started_at.isoformat())
        self.assertEqual(data['endedAt'], self.test_session.ended_at.isoformat())
        self.assertEqual(data['createdAt'], self.test_session.created_at.isoformat())
        self.assertEqual(data['updatedAt'], self.test_session.updated_at.isoformat())
        self.assertEqual(data['allowAdminAccess'], False)
        self.assertEqual(data['hasReviewed'], True)
