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
from app.dependencies import get_db_session, require_admin, require_user
from app.main import app
from app.models import Review, Session, SessionStatus, UserProfile
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
        app.dependency_overrides[require_admin] = lambda: self.test_user

        self.client = TestClient(app)

        # Populate dummy data
        conversation_categories = get_dummy_conversation_categories()
        self.db.add_all(conversation_categories)
        self.db.commit()

        self.conversation_scenarios = get_dummy_conversation_scenarios(
            [self.test_user, self.test_user], conversation_categories
        )

        self.db.add_all(self.conversation_scenarios)
        self.db.commit()

        # Create a test session
        self.test_session = Session(
            id=uuid4(),
            scenario_id=self.conversation_scenarios[0].id,
            scheduled_at=datetime.now(),
            started_at=datetime.now(),
            ended_at=datetime.now(),
            status=SessionStatus.completed,
        )
        self.db.add(self.test_session)
        self.db.commit()

    def tearDown(self) -> None:
        self.db.rollback()
        for table in reversed(SQLModel.metadata.sorted_tables):
            self.db.execute(table.delete())
        self.db.commit()
        self.db.close()

    def _create_multiple_dummy_reviews(
        self, user: UserProfile, num_reviews: int, rating: int
    ) -> None:
        """
        Helper method to create multiple dummy reviews for testing.
        """
        for _ in range(num_reviews):
            dummy_session = Session(
                id=uuid4(),
                scenario_id=self.conversation_scenarios[0].id,
                scheduled_at=datetime.now(),
                started_at=datetime.now(),
                ended_at=datetime.now(),
                status=SessionStatus.completed,
            )
            self.db.add(dummy_session)
            self.db.commit()

            dummy_review = Review(
                id=uuid4(),
                user_id=user.id,
                session_id=dummy_session.id,
                rating=rating,
                comment='Dummy review',
            )

            self.db.add(dummy_review)
            self.db.commit()

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

    def test_get_reviews_route_sort_and_limit(self) -> None:
        self._create_multiple_dummy_reviews(self.test_user, 2, 5)
        self._create_multiple_dummy_reviews(self.test_user, 2, 4)
        self._create_multiple_dummy_reviews(self.test_user, 1, 3)
        self._create_multiple_dummy_reviews(self.test_user, 1, 2)
        self._create_multiple_dummy_reviews(self.test_user, 1, 1)

        response = self.client.get('/review', params={'limit': 5, 'sort': 'highest'})
        self.assertEqual(response.status_code, 200)
        reviews = response.json()
        self.assertEqual(len(reviews), 5)
        self.assertTrue(
            all(reviews[i]['rating'] >= reviews[i + 1]['rating'] for i in range(len(reviews) - 1))
        )

        response = self.client.get('/review', params={'limit': 5, 'sort': 'lowest'})
        self.assertEqual(response.status_code, 200)
        reviews = response.json()
        self.assertEqual(len(reviews), 5)
        self.assertTrue(
            all(reviews[i]['rating'] <= reviews[i + 1]['rating'] for i in range(len(reviews) - 1))
        )

    def test_get_reviews_route_pagination(self) -> None:
        self._create_multiple_dummy_reviews(self.test_user, 2, 5)
        self._create_multiple_dummy_reviews(self.test_user, 2, 4)
        self._create_multiple_dummy_reviews(self.test_user, 1, 3)
        self._create_multiple_dummy_reviews(self.test_user, 1, 2)
        self._create_multiple_dummy_reviews(self.test_user, 1, 1)

        response = self.client.get('/review', params={'page': 1, 'page_size': 3, 'sort': 'newest'})
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn('reviews', data)
        self.assertEqual(len(data['reviews']), 3)
        self.assertTrue(
            all(
                data['reviews'][i]['date'] >= data['reviews'][i + 1]['date']
                for i in range(len(data['reviews']) - 1)
            )
        )
        self.assertEqual(data['pagination']['currentPage'], 1)
        self.assertEqual(data['pagination']['totalPages'], 3)
        self.assertEqual(data['pagination']['totalCount'], 7)
        self.assertEqual(data['pagination']['pageSize'], 3)
        self.assertAlmostEqual(data['ratingStatistics']['average'], 3.43)
