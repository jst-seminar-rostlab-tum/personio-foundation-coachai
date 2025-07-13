import unittest
from collections.abc import Generator
from datetime import datetime

from fastapi.security import HTTPBearer
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool.impl import StaticPool
from sqlmodel import Session as DBSession
from sqlmodel import SQLModel, create_engine

from app.data.dummy_data import (
    get_dummy_conversation_categories,
    get_dummy_conversation_scenarios,
    get_dummy_user_profiles,
)
from app.dependencies import JWTPayload, get_db_session, security, verify_jwt
from app.main import app
from app.models.conversation_scenario import ConversationScenario
from app.schemas.conversation_scenario import ConversationScenarioRead


class TestConversationScenarioRoute(unittest.TestCase):
    """
    Test suite for the Conversation Scenario API route and service logic.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up the test environment by creating an in-memory SQLite database
        and initializing a FastAPI app with the conversation scenario router.
        """
        # Create an in-memory SQLite database for testing
        cls.engine = create_engine(
            'sqlite:///:memory:', connect_args={'check_same_thread': False}, poolclass=StaticPool
        )
        SQLModel.metadata.create_all(cls.engine)  # Create all tables in the database
        cls.SessionLocal = sessionmaker(bind=cls.engine, class_=DBSession)

        # Override the database dependency to use the in-memory database
        def override_get_db() -> Generator[DBSession, None, None]:
            with cls.SessionLocal() as session:
                yield session

        app.dependency_overrides[get_db_session] = override_get_db

        # Override verify_jwt to always return a payload with sub=test_user.id
        app.dependency_overrides[verify_jwt] = lambda: JWTPayload(sub='test_user_id')

        # Initialize the test client
        cls.client = TestClient(app)

    def setUp(self) -> None:
        """
        Set up the database and test client before each test.
        This includes clearing and recreating the database tables and populating dummy data.
        """
        self.db = self.SessionLocal()

        # Generate dummy data
        self.dummy_user_profiles = get_dummy_user_profiles()
        self.dummy_categories = get_dummy_conversation_categories()
        self.dummy_scenarios = get_dummy_conversation_scenarios(
            user_profiles=self.dummy_user_profiles, categories=self.dummy_categories
        )

        # Add dummy data to the database
        self.db.add_all(self.dummy_user_profiles)
        self.db.add_all(self.dummy_categories)
        self.db.add_all(self.dummy_scenarios)
        self.db.commit()

    def tearDown(self) -> None:
        """
        Roll back the database session and close it after each test.
        """
        self.db.rollback()
        for table in reversed(SQLModel.metadata.sorted_tables):
            self.db.execute(table.delete())
        self.db.commit()
        self.db.close()

    def test_get_conversation_scenarios(self) -> None:
        """
        Test retrieving all conversation scenarios.
        This ensures that the API returns the correct data for all scenarios in the database.
        """
        response = self.client.get('/conversation-scenarios')

        # Assert the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Parse the response data
        data = response.json()

        # Assert the number of scenarios matches the dummy data
        self.assertEqual(len(data), len(self.dummy_scenarios))

        # Validate each scenario in the response against the schema
        for i, scenario in enumerate(self.dummy_scenarios):
            current_data = ConversationScenarioRead(**data[i])  # Validate against the schema

            # Validate the `scenario` field
            self.assertEqual(current_data.scenario.id, scenario.id)
            self.assertEqual(current_data.scenario.category_id, scenario.category_id)
            self.assertEqual(current_data.scenario.language_code, scenario.language_code)
            self.assertIsInstance(current_data.scenario.created_at, datetime)
            self.assertIsInstance(current_data.scenario.updated_at, datetime)

            # Validate the `transcript` field
            self.assertIsInstance(current_data.transcript, list)

    def test_get_conversation_scenarios_empty(self) -> None:
        """
        Test retrieving conversation scenarios when none exist.
        This ensures that the API returns an empty list when no scenarios are present.
        """
        # Clear the database
        self.db.query(ConversationScenario).delete()
        self.db.commit()

        response = self.client.get('/conversation-scenarios')

        # Assert the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Assert the response data is an empty list
        self.assertEqual(response.json(), [])

    def test_get_conversation_scenario_unauthenticated(self) -> None:
        app.dependency_overrides.pop(security, HTTPBearer())
        app.dependency_overrides.pop(verify_jwt, None)

        response = self.client.get('/conversation-scenarios')
        self.assertEqual(response.status_code, 403)
        # depending on FastAPI version/detail text:
        # self.assertIn('Not authenticated', response.json()['detail'])


if __name__ == '__main__':
    unittest.main()
