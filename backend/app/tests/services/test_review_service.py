import unittest
from collections.abc import Generator
from datetime import datetime
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool.impl import StaticPool
from sqlmodel import Session as DBSession
from sqlmodel import SQLModel, create_engine, select

from app.data import (
    get_dummy_conversation_categories,
    get_dummy_conversation_scenarios,
    get_dummy_user_profiles,
)
from app.dependencies import JWTPayload, get_db_session, verify_jwt
from app.enums.session_status import SessionStatus
from app.models import Session, UserProfile
from app.models.review import Review
from app.schemas import PaginatedReviewRead, ReviewCreate
from app.services.review_service import ReviewService


class TestReviewService(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up the test environment by creating an in-memory SQLite database.
        """
        # Create an in-memory SQLite database for testing
        cls.engine = create_engine(
            'sqlite:///:memory:', connect_args={'check_same_thread': False}, poolclass=StaticPool
        )
        SQLModel.metadata.create_all(cls.engine)  # Create all tables in the database
        cls.SessionLocal = sessionmaker(bind=cls.engine, class_=DBSession)

        # Initialize a new FastAPI app for testing
        cls.app = FastAPI()

        # Override the database dependency to use the in-memory database
        def override_get_db() -> Generator[DBSession]:
            with cls.SessionLocal() as session:
                yield session

        cls.app.dependency_overrides[get_db_session] = override_get_db

    def setUp(self) -> None:
        """
        Set up the database session and populate dummy data before each test.
        """
        # Clear and recreate the database tables before each test
        SQLModel.metadata.drop_all(self.engine)
        SQLModel.metadata.create_all(self.engine)

        # Create a new database session
        self.db = self.SessionLocal()

        # Mock the authenticated user
        self.test_users = get_dummy_user_profiles()  # Use the first dummy user
        self.db.add_all(self.test_users)
        self.db.commit()

        self.normal_user = self.test_users[0]  # Use the first dummy user as the normal user
        self.admin_user = self.test_users[1]  # Use the second dummy user as the admin user

        # Populate dummy conversation categories

        # Initialize the service
        self.service = ReviewService(self.db)

        # Override the require_user dependency to return the mocked user
        self.app.dependency_overrides[verify_jwt] = lambda: JWTPayload(sub=self.normal_user.id.hex)

        # Initialize the test client
        self.client = TestClient(self.app)

        # Create a test session for the review
        self.conversation_categories = get_dummy_conversation_categories()
        self.db.add_all(self.conversation_categories)
        self.db.commit()

        self.conversation_scenarios = get_dummy_conversation_scenarios(
            self.test_users, self.conversation_categories
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
        """
        Roll back the database session and close it after each test.
        """
        self.db.rollback()
        self.db.close()

    def test_create_general_review(self) -> None:
        """
        Test creating a general review (no session).
        """
        review = ReviewCreate(session_id=None, rating=5, comment='Great session!')
        response = self.service.create_review(review, self.normal_user)
        self.assertEqual(response.message, 'Review submitted successfully')
        self.assertIsNotNone(response.review_id)
        created_review = self.db.exec(select(Review).where(Review.id == response.review_id)).first()
        self.assertIsNotNone(created_review)
        self.assertEqual(created_review.user_id, self.normal_user.id)
        self.assertEqual(created_review.rating, review.rating)
        self.assertEqual(created_review.comment, review.comment)
        self.assertIsNone(created_review.session_id)

    def test_create_session_review(self) -> None:
        """
        Test creating a review for a specific session.
        """
        review = ReviewCreate(session_id=self.test_session.id, rating=5, comment='Great session!')
        response = self.service.create_review(review, self.normal_user)
        self.assertEqual(response.message, 'Review submitted successfully')
        self.assertIsNotNone(response.review_id)
        created_review = self.db.exec(select(Review).where(Review.id == response.review_id)).first()
        self.assertIsNotNone(created_review)
        self.assertEqual(created_review.user_id, self.normal_user.id)
        self.assertEqual(created_review.rating, review.rating)
        self.assertEqual(created_review.comment, review.comment)
        self.assertEqual(created_review.session_id, self.test_session.id)

    def test_duplicate_review_for_same_session(self) -> None:
        """
        Test that submitting a duplicate review for the same session raises an exception.
        """
        review = ReviewCreate(session_id=self.test_session.id, rating=5, comment='Great session!')
        self.service.create_review(review, self.normal_user)
        with self.assertRaises(HTTPException) as context:
            self.service.create_review(review, self.normal_user)
        self.assertEqual(context.exception.status_code, 409)
        self.assertEqual(
            context.exception.detail, 'User has already submitted a review for this session.'
        )

    def test_invalid_rating_review(self) -> None:
        """
        Test that submitting a review with an out-of-range rating raises an exception.
        """
        invalid_review = ReviewCreate(rating=6, comment='Great session!')
        with self.assertRaises(HTTPException) as context:
            self.service.create_review(invalid_review, self.normal_user)
        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, 'Rating must be between 1 and 5')

    def test_create_review_with_invalid_session_id(self) -> None:
        review = ReviewCreate(
            session_id=uuid4(),  # Invalid session ID
            rating=5,
            comment='Great session!',
        )
        with self.assertRaises(HTTPException) as context:
            self.service.create_review(review, self.normal_user)
        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, 'Session not found')

    def test_create_review_with_invalid_scenario_id(self) -> None:
        """
        Test that a user cannot create a review for a session with an invalid scenario ID.
        """
        # Create a session with an invalid scenario ID
        invalid_scenario_session = Session(
            id=uuid4(),
            scenario_id=uuid4(),  # Use a non-existent scenario ID
            scheduled_at=datetime.now(),
            started_at=datetime.now(),
            ended_at=datetime.now(),
            status=SessionStatus.completed,
        )
        self.db.add(invalid_scenario_session)
        self.db.commit()

        review = ReviewCreate(
            session_id=invalid_scenario_session.id, rating=5, comment='Great session!'
        )
        with self.assertRaises(HTTPException) as context:
            self.service.create_review(review, self.normal_user)
        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, 'No conversation scenario found for the session')

    def test_create_review_without_permission(self) -> None:
        """
        Test that a normal user cannot create a review for a scenario that does not belong to them.
        First, use admin_user to create a scenario,
        then let normal_user try to create a review for a session under that scenario,
        which should be rejected.
        """

        admin_scenario = self.conversation_scenarios[1]  # Use the scenario for admin
        self.db.add(admin_scenario)
        self.db.commit()

        # Create a session belonging to admin_scenario
        unauthorized_session = Session(
            id=uuid4(),
            scenario_id=admin_scenario.id,
            scheduled_at=datetime.now(),
            started_at=datetime.now(),
            ended_at=datetime.now(),
            status=SessionStatus.completed,
        )
        self.db.add(unauthorized_session)
        self.db.commit()

        # normal_user tries to create a review for this session
        review = ReviewCreate(
            session_id=unauthorized_session.id, rating=5, comment='Great session!'
        )
        with self.assertRaises(HTTPException) as context:
            self.service.create_review(review, self.normal_user)
        self.assertEqual(context.exception.status_code, 403)
        self.assertEqual(
            context.exception.detail,
            'Not your session: You do not have permission to create this review.',
        )

    def test_create_review_as_scenario_admin(self) -> None:
        """
        Test that a scenario admin (admin user) can create a review for a session they manage.
        """
        # Assume the second user is admin
        scenario_admin = self.admin_user
        # Set the admin user as the owner of the scenario
        self.conversation_scenarios[0].user_id = scenario_admin.id
        self.db.add(self.conversation_scenarios[0])
        self.db.commit()

        # Create a session belonging to this scenario
        admin_session = Session(
            id=uuid4(),
            scenario_id=self.conversation_scenarios[0].id,
            scheduled_at=datetime.now(),
            started_at=datetime.now(),
            ended_at=datetime.now(),
            status=SessionStatus.completed,
        )
        self.db.add(admin_session)
        self.db.commit()

        review = ReviewCreate(
            session_id=admin_session.id, rating=5, comment='Admin review for own scenario session'
        )
        # The admin user should be able to successfully create a review
        response = self.service.create_review(review, scenario_admin)
        self.assertEqual(response.message, 'Review submitted successfully')
        self.assertIsNotNone(response.review_id)

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

            dummy_review = ReviewCreate(
                session_id=dummy_session.id, rating=rating, comment='Dummy review'
            )
            self.service.create_review(dummy_review, user)

    def test_get_reviews_with_limit(self) -> None:
        self._create_multiple_dummy_reviews(self.normal_user, 2, 5)
        self._create_multiple_dummy_reviews(self.normal_user, 2, 4)
        self._create_multiple_dummy_reviews(self.normal_user, 1, 3)
        self._create_multiple_dummy_reviews(self.normal_user, 1, 2)
        self._create_multiple_dummy_reviews(self.normal_user, 1, 1)

        reviews = self.service.get_reviews(limit=5, sort='highest')
        self.assertEqual(len(reviews), 5)
        self.assertTrue(
            all(reviews[i].rating >= reviews[i + 1].rating for i in range(len(reviews) - 1))
        )

        reviews = self.service.get_reviews(limit=5, sort='lowest')
        self.assertEqual(len(reviews), 5)
        self.assertTrue(
            all(reviews[i].rating <= reviews[i + 1].rating for i in range(len(reviews) - 1))
        )

        reviews = self.service.get_reviews(limit=5, sort='newest')
        self.assertEqual(len(reviews), 5)
        self.assertTrue(
            all(reviews[i].date >= reviews[i + 1].date for i in range(len(reviews) - 1))
        )

        reviews = self.service.get_reviews(limit=5, sort='oldest')
        self.assertEqual(len(reviews), 5)
        self.assertTrue(
            all(reviews[i].date <= reviews[i + 1].date for i in range(len(reviews) - 1))
        )

    def test_get_reviews_with_pagination(self) -> None:
        self._create_multiple_dummy_reviews(self.normal_user, 2, 5)
        self._create_multiple_dummy_reviews(self.normal_user, 2, 4)
        self._create_multiple_dummy_reviews(self.normal_user, 1, 3)
        self._create_multiple_dummy_reviews(self.normal_user, 1, 2)
        self._create_multiple_dummy_reviews(self.normal_user, 1, 1)
        reviews = self.service.get_reviews(page=1, page_size=3, sort='newest', limit=None)
        self.assertIsInstance(reviews, PaginatedReviewRead)
        self.assertEqual(len(reviews.reviews), 3)
        self.assertTrue(
            all(
                reviews.reviews[i].date >= reviews.reviews[i + 1].date
                for i in range(len(reviews.reviews) - 1)
            )
        )
        self.assertEqual(reviews.pagination['currentPage'], 1)
        self.assertEqual(reviews.pagination['totalPages'], 3)
        self.assertEqual(reviews.pagination['totalCount'], 7)
        self.assertEqual(reviews.pagination['pageSize'], 3)
        self.assertEqual(reviews.rating_statistics.average, 3.43)
