import unittest

from fastapi.testclient import TestClient

from app.main import app


class TestSignedUrlsRoute(unittest.TestCase):
    """Test suite guarding the shape of the signed-urls router.

    The audio signed-url endpoint was removed because it had no consumer and
    generated a signed URL for any client-supplied filename without verifying
    that the caller owned the underlying object. The legitimate audio URL is
    served, ownership-checked, through the session feedback response instead.
    These tests ensure the audio endpoint stays gone while the shared-document
    endpoint remains available.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """Initialize the test client for the FastAPI app."""
        cls.client = TestClient(app)

    def _registered_paths(self) -> set[str]:
        """Return the set of paths currently registered on the app."""
        return {getattr(route, 'path', None) for route in app.routes}

    def test_audio_signed_url_endpoint_is_removed(self) -> None:
        """The audio signed-url endpoint must not be registered."""
        self.assertNotIn('/signed-urls/audio', self._registered_paths())

    def test_audio_signed_url_request_returns_404(self) -> None:
        """Requesting the removed audio endpoint returns 404 Not Found."""
        response = self.client.get('/signed-urls/audio', params={'filename': 'anything.mp3'})
        self.assertEqual(response.status_code, 404)

    def test_docs_signed_url_endpoint_is_retained(self) -> None:
        """The shared-document signed-url endpoint must remain registered."""
        self.assertIn('/signed-urls/docs', self._registered_paths())


if __name__ == '__main__':
    unittest.main()
