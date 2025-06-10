import os
from unittest.mock import MagicMock, patch

import pytest
from dotenv import load_dotenv
from google.genai.types import Content, Part

from app.connections.gemini_client import (
    GeminiStreamConnectionError,
    get_client,
)

load_dotenv()

AUDIO_SAMPLE_DIR = os.path.join(os.path.dirname(__file__), 'audio_samples')
FIRING_EXAMPLE_PCM_PATH = os.path.join(AUDIO_SAMPLE_DIR, 'short-firing-example.wav')


def test_gemini_client_connection() -> None:
    """Test if Gemini client can be successfully instantiated and connected"""
    client = get_client()
    assert client is not None
    # Try to trigger the API call to verify the connection
    print(
        client.models.generate_content(
            model='gemini-2.0-flash-001',
            contents=[Content(role='user', parts=[Part(text='Who are you?')])],
        )
    )


@patch('app.connections.gemini_client.genai.Client', side_effect=Exception('Invalid key'))
@patch.dict('os.environ', {'GEMINI_API_KEY': 'invalid_api_key'})
def test_gemini_client_connection_error(mock_client: MagicMock) -> None:
    """Test if Gemini client connection error is raised correctly"""

    # clear the singleton cache
    if hasattr(get_client, '_client'):
        del get_client._client

    # Trigger the function and expect the error
    with pytest.raises(GeminiStreamConnectionError):
        get_client()
