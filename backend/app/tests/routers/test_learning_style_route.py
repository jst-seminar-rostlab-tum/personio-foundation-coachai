import unittest
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, create_engine

from app.main import app


class TestLearningStyleRoute(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.engine = create_engine('sqlite:///:memory:', echo=False)
        cls.Session = sessionmaker(bind=cls.engine)
        SQLModel.metadata.create_all(bind=cls.engine)
        cls.client = TestClient(app)

    def setUp(self) -> None:
        self.session = self.Session()

    def tearDown(self) -> None:
        self.session.close()

    def test_create_learning_style_success(self) -> None:
        response = self.client.post("/learning-styles", json={
            "language_code": "en",
            "label": "Visual",
            "description": "Prefers visual learning."
        })
        assert response.status_code == 200, f"Unexpected status: {response.status_code}"
        data = response.json()
        assert data["language_code"] == "en"
        assert data["label"] == "Visual"
        assert data["description"] == "Prefers visual learning."
        assert "id" in data, "Missing ID in response"

    def test_create_learning_style_duplicate_should_fail(self) -> None:
        ls_id = str(uuid4())
        payload = {
            "id": ls_id,
            "language_code": "en",
            "label": "Auditory",
            "description": "Prefers auditory learning."
        }
        r1 = self.client.post("/learning-styles", json=payload)
        assert r1.status_code == 200, f"Initial creation failed: {r1.status_code}"
        r2 = self.client.post("/learning-styles", json=payload)
        assert r2.status_code == 400
        assert r2.json() == {"detail": "LearningStyle with this language already exists."}

    def test_get_learning_styles_with_fallback(self) -> None:
        ls_id = str(uuid4())
        self.client.post("/learning-styles", json={
            "id": ls_id,
            "language_code": "",
            "label": "Kinesthetic",
            "description": "Prefers physical activities."
        })
        response = self.client.get("/learning-styles?lang=de")
        assert response.status_code == 200
        ids = [item["id"] for item in response.json()]
        assert ls_id in ids, f"{ls_id} not found in fallback results"

    def test_update_learning_style(self) -> None:
        ls_id = str(uuid4())
        self.client.post("/learning-styles", json={
            "id": ls_id,
            "language_code": "en",
            "label": "Old Label",
            "description": "Old Description"
        })
        update = {
            "language_code": "en",
            "label": "Updated Label",
            "description": "Updated Description"
        }
        response = self.client.put(f"/learning-styles/{ls_id}?lang=en", json=update)
        assert response.status_code == 200
        data = response.json()
        assert data["label"] == "Updated Label"
        assert data["description"] == "Updated Description"

    def test_update_nonexistent_learning_style(self) -> None:
        random_id = str(uuid4())
        update = {
            "language_code": "en",
            "label": "Doesn't Matter",
            "description": "Should not exist"
        }
        response = self.client.put(f"/learning-styles/{random_id}?lang=en", json=update)
        assert response.status_code == 404
        assert response.json()["detail"] == "Learning style not found"

    def test_delete_learning_style(self) -> None:
        ls_id = str(uuid4())
        self.client.post("/learning-styles", json={
            "id": ls_id,
            "language_code": "en",
            "label": "To Be Deleted",
            "description": "Temporary"
        })
        response = self.client.delete(f"/learning-styles/{ls_id}?lang=en")
        assert response.status_code == 200
        assert response.json() == {"message": "Learning style deleted successfully"}

        # confirm deletion
        response = self.client.delete(f"/learning-styles/{ls_id}?lang=en")
        assert response.status_code == 404
if __name__ == '__main__':
    unittest.main()