import unittest
from collections.abc import Generator
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool.impl import StaticPool
from sqlmodel import Session as DBSession
from sqlmodel import SQLModel, create_engine, select

from app.data.dummy_data import get_dummy_conversation_categories, get_dummy_user_profiles
from app.dependencies import get_db_session, require_user
from app.models.conversation_category import ConversationCategory
from app.routers.conversation_category_route import router as conversation_category_router
from app.schemas.conversation_category import ConversationCategoryRead
from app.services.conversation_category_service import ConversationCategoryService


class TestConversationCategoryRoute(unittest.TestCase):
    """
    Test suite for the Conversation Category API route and service logic.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up the test environment by creating an in-memory SQLite database
        and initializing a FastAPI app with the conversation category router.
        """
        # Create an in-memory SQLite database for testing
        cls.engine = create_engine(
            'sqlite:///:memory:', connect_args={'check_same_thread': False}, poolclass=StaticPool
        )
        SQLModel.metadata.create_all(cls.engine)  # Create all tables in the database
        cls.SessionLocal = sessionmaker(bind=cls.engine, class_=DBSession)

        # Initialize a new FastAPI app for testing
        cls.app = FastAPI()

        # Include the conversation category router
        cls.app.include_router(conversation_category_router)

        # Override the database dependency to use the in-memory database
        def override_get_db() -> Generator[DBSession, None, None]:
            with cls.SessionLocal() as session:
                yield session

        cls.app.dependency_overrides[get_db_session] = override_get_db

    def setUp(self) -> None:
        """
        Set up the database and test client before each test.
        This includes clearing and recreating the database tables and populating dummy data.
        """
        # Clear and recreate the database tables before each test
        SQLModel.metadata.drop_all(self.engine)
        SQLModel.metadata.create_all(self.engine)

        # Create a new database session
        self.db = self.SessionLocal()

        # Mock the authenticated user
        self.test_user = get_dummy_user_profiles()[0]  # Use the first dummy user
        self.db.add(self.test_user)
        self.db.commit()

        # Override the require_user dependency to return the mocked user
        self.app.dependency_overrides[require_user] = lambda: self.test_user

        # Initialize the test client
        self.client = TestClient(self.app)

        # Populate the database with dummy conversation categories
        self.dummy_categories = get_dummy_conversation_categories()
        self.db.add_all(self.dummy_categories)
        self.db.commit()

    def tearDown(self) -> None:
        """
        Roll back the database session and close it after each test.
        """
        self.db.rollback()
        self.db.close()

    # Endpoint Tests
    def test_get_conversation_categories(self) -> None:
        """
        Test retrieving all conversation categories.
        This ensures that the API returns the correct data for all categories in the database.
        """
        response = self.client.get('/conversation-categories')

        # Assert the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Parse the response data
        data = response.json()

        # Assert the number of categories matches the dummy data
        self.assertEqual(len(data), len(self.dummy_categories))

        # Validate each category in the response against the dummy data
        for i, category in enumerate(self.dummy_categories):
            current_data = ConversationCategoryRead(**data[i])  # Validate against the schema
            self.assertEqual(current_data.id, category.id)
            self.assertEqual(current_data.name, category.name)
            self.assertEqual(current_data.is_custom, category.is_custom)
            self.assertEqual(current_data.language_code, category.language_code)
            self.assertIsInstance(current_data.created_at, datetime)
            self.assertIsInstance(current_data.updated_at, datetime)

    def test_get_conversation_categories_empty(self) -> None:
        """
        Test retrieving conversation categories when none exist in the database.
        This ensures that the API returns an empty list when no categories are present.
        """
        # Clear all categories from the database
        stmt = select(ConversationCategory)
        results = self.db.exec(stmt).all()
        for category in results:
            self.db.delete(category)
        self.db.commit()

        # Send a GET request to the conversation categories endpoint
        response = self.client.get('/conversation-categories')

        # Assert the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Assert the response data is an empty list
        data = response.json()
        self.assertEqual(data, [])

    def test_get_conversation_categories_invalid_user(self) -> None:
        """
        Test retrieving conversation categories with an invalid user.
        This ensures that the API returns a 403 Forbidden error.
        """

        # Override the require_user dependency to simulate no user
        def mock_require_user() -> HTTPException:
            raise HTTPException(status_code=403, detail='Not authenticated')

        self.app.dependency_overrides[require_user] = mock_require_user

        # Send a GET request to the conversation categories endpoint
        response = self.client.get('/conversation-categories')

        # Assert the response status code is 403 (Forbidden)
        self.assertEqual(response.status_code, 403)

    # Service Logic Tests
    def test_fetch_all_conversation_categories(self) -> None:
        """
        Test the service logic for fetching all conversation categories.
        This ensures that the service returns the correct data from the database.
        """
        service = ConversationCategoryService(self.db)
        categories = service.fetch_all_conversation_categories()

        # Assert the number of categories matches the dummy data
        self.assertEqual(len(categories), len(self.dummy_categories))

        # Validate each category in the service response against the dummy data
        for i, category in enumerate(self.dummy_categories):
            self.assertEqual(categories[i].id, category.id)
            self.assertEqual(categories[i].name, category.name)
            self.assertEqual(categories[i].is_custom, category.is_custom)
            self.assertEqual(categories[i].language_code, category.language_code)

    def test_fetch_all_conversation_categories_empty(self) -> None:
        """
        Test the service logic for fetching all conversation categories when none exist.
        This ensures that the service returns an empty list when no categories are present.
        """
        # Clear all categories from the database
        stmt = select(ConversationCategory)
        results = self.db.exec(stmt).all()
        for category in results:
            self.db.delete(category)
        self.db.commit()

        service = ConversationCategoryService(self.db)
        categories = service.fetch_all_conversation_categories()

        # Assert the service returns an empty list
        self.assertEqual(categories, [])


if __name__ == '__main__':
    unittest.main()
