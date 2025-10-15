import unittest
from collections.abc import Generator
from datetime import datetime

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool.impl import StaticPool
from sqlmodel import Session as DBSession
from sqlmodel import SQLModel, create_engine, select

from app.data.dummy_data import get_dummy_conversation_categories, get_dummy_user_data
from app.dependencies import get_db_session, require_user
from app.models.conversation_category import ConversationCategory
from app.schemas.conversation_category import ConversationCategoryRead
from app.services.conversation_category_service import ConversationCategoryService


class TestConversationCategoryService(unittest.TestCase):
    """
    Unit tests for the ConversationCategoryService.
    """

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
        self.test_user = get_dummy_user_data()[0].user_profile  # Use the first dummy user
        self.db.add(self.test_user)
        self.db.commit()

        # Populate the database with dummy conversation categories
        self.dummy_categories = get_dummy_conversation_categories()
        self.db.add_all(self.dummy_categories)
        self.db.commit()

        # Initialize the service
        self.service = ConversationCategoryService(self.db)

        # Override the require_user dependency to return the mocked user
        self.app.dependency_overrides[require_user] = lambda: self.test_user

        # Initialize the test client
        self.client = TestClient(self.app)

    def tearDown(self) -> None:
        """
        Roll back the database session and close it after each test.
        """
        self.db.rollback()
        self.db.close()

    def test_fetch_all_conversation_categories(self) -> None:
        """
        Test fetching all conversation categories.
        This ensures that the service returns the correct data from the database.
        """
        # Call the service method
        categories = self.service.fetch_all_conversation_categories()

        # Assert the number of categories matches the dummy data
        self.assertEqual(len(categories), len(self.dummy_categories))

        # Validate each category in the service response against the dummy data
        for i, category in enumerate(self.dummy_categories):
            self.assertEqual(categories[i].id, category.id)
            self.assertEqual(categories[i].name, category.name)
            self.assertEqual(categories[i].is_custom, category.is_custom)
            self.assertEqual(categories[i].language_code, category.language_code)
            self.assertIsInstance(categories[i].created_at, datetime)
            self.assertIsInstance(categories[i].updated_at, datetime)

    def test_fetch_all_conversation_categories_empty(self) -> None:
        """
        Test fetching all conversation categories when none exist.
        This ensures that the service returns an empty list when no categories are present.
        """
        # Clear all categories from the database
        stmt = select(ConversationCategory)
        results = self.db.exec(stmt).all()
        for category in results:
            self.db.delete(category)
        self.db.commit()

        # Call the service method
        categories = self.service.fetch_all_conversation_categories()

        # Assert the service returns an empty list
        self.assertEqual(categories, [])

    def test_fetch_all_conversation_categories_schema_validation(self) -> None:
        """
        Test that the service returns data conforming to the ConversationCategoryRead schema.
        """
        # Call the service method
        categories = self.service.fetch_all_conversation_categories()

        # Validate each category against the schema
        for category in categories:
            self.assertIsInstance(category, ConversationCategoryRead)


if __name__ == '__main__':
    unittest.main()
