import unittest
from collections.abc import Generator
from datetime import datetime
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool.impl import StaticPool
from sqlmodel import Session as DBSession
from sqlmodel import SQLModel, create_engine

from app.data.dummy_data import get_dummy_conversation_categories, get_dummy_conversation_scenarios
from app.dependencies import get_db_session, require_user
from app.main import app
from app.models import Session, SessionStatus, UserProfile
from app.models.user_profile import AccountRole


class TestReviewRoute(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # Create an in-memory SQLite database for testing
        cls.engine = create_engine(
            'sqlite:///:memory:', connect_args={'check_same_thread': False}, poolclass=StaticPool
        )
        SQLModel.metadata.create_all(cls.engine)
        cls.SessionLocal = sessionmaker(bind=cls.engine, class_=DBSession)

    def setUp(self) -> None:
        self.db = self.SessionLocal()

        def override_get_db() -> Generator[DBSession, None, None]:
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

    def tearDown(self) -> None:
        self.db.rollback()
        self.db.close()

    def test_post_review(self) -> None:
        review_payload = {
            'sessionId': str(self.test_session.id),
            'rating': 6,
            'comment': 'Great session!',
            'allowAdminAccess': False,
        }
        # Test invalid rating
        response = self.client.post('/review', json=review_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['detail'], 'Rating must be between 1 and 5')

        # Test valid review
        review_payload['rating'] = 5
        response = self.client.post('/review', json=review_payload)
        self.assertEqual(response.status_code, 200)

        # Test duplicate review
        response = self.client.post('/review', json=review_payload)
        self.assertEqual(response.status_code, 409)
