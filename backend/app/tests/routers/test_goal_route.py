import unittest
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm.session import sessionmaker
from sqlmodel import SQLModel, create_engine

from app.main import app


class TestGoalRoute(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # initial setup for the db
        cls.engine = create_engine('sqlite:///:memory:', echo=False)
        cls.Session = sessionmaker(bind=cls.engine)
        SQLModel.metadata.create_all(bind=cls.engine)
        cls.client = TestClient(app)

    def setUp(self) -> None:
        # create a new session for each test
        self.session = self.Session()

    def tearDown(self) -> None:
        # close the session after each test
        self.session.close()

    def test_create_goal_success(self) -> None:
        # first insert a goal
        response = self.client.post("/goals", json={
            "language_code": "en",
            "label": "Test Goal",
            "description": "Test goal description"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["languageCode"] == "en"

        # add another goal with the same ID but different language
        response = self.client.post("/goals", json={
            "id": data["id"],
            "language_code": "de",
            "label": "Test Ziel",
            "description": "Test Zielbeschreibung"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["languageCode"] == "de"
        assert data["id"] == response.json()["id"]

        # add another goal with the same ID and language, should fail
        response = self.client.post("/goals", json={
            "id": data["id"],
            "language_code": "de",
            "label": "Test Ziel",
            "description": "Test Zielbeschreibung"
        })
        assert response.status_code == 400
        assert response.json() == {"detail": "Goal with this language already exists."}

    def test_create_goal_invalid_language(self) -> None:
        # try to create a goal with an invalid language code
        response = self.client.post("/goals", json={
            "language_code": "dummy",
            "label": "Test Goal",
            "description": "Test goal description"
        })
        assert response.status_code == 400
        assert response.json() == {"detail": "Language code must be 'en' or 'de'."}

    def test_get_goals_returns_created_goal(self) -> None:
        goal_id = str(uuid4())
        payload = {
            "id": goal_id,
            "language_code": "en",
            "label": "Read Books",
            "description": "Build a reading habit"
        }
        self.client.post("/goals", json=payload)

        response = self.client.get("/goals?lang=en")
        assert response.status_code == 200
        goals = response.json()
        assert any(g["id"] == goal_id for g in goals)

        response = self.client.get("/goals?lang=de")
        assert response.status_code == 200
        goals = response.json()
        assert any(g["id"] == goal_id for g in goals)

    def test_get_goals_returns_created_goal_fallback(self) -> None:
        goal_id = str(uuid4())
        payload = {
            "id": goal_id,
            "label": "Read Books",
            "language_code": "",
            "description": "Build a reading habit"
        }
        self.client.post("/goals", json=payload)

        response = self.client.get("/goals?lang=en")
        assert response.status_code == 200
        goals = response.json()
        assert any(g["id"] == goal_id for g in goals)

        response = self.client.get("/goals?lang=de")
        assert response.status_code == 200
        goals = response.json()
        assert any(g["id"] == goal_id for g in goals)


if __name__ == '__main__':
    unittest.main()