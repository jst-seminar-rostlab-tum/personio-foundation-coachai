import importlib

import pytest

from app.connections import gemini_client


@pytest.fixture
def dev_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set stage to 'dev' and reload module."""
    monkeypatch.setattr('app.connections.gemini_client.settings.stage', 'dev')
    importlib.reload(gemini_client)
    monkeypatch.setattr(gemini_client, 'ENABLE_AI', True)


@pytest.fixture
def prod_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set stage to 'prod' and reload module."""
    monkeypatch.setattr('app.connections.gemini_client.settings.stage', 'prod')
    importlib.reload(gemini_client)
    monkeypatch.setattr(gemini_client, 'ENABLE_AI', True)


@pytest.fixture(autouse=True)
def _clean_client_cache() -> None:
    """Clears any cached Gemini clients before each test to ensure a clean state."""
    if hasattr(gemini_client.get_client, '_client'):
        delattr(gemini_client.get_client, '_client')
    if hasattr(gemini_client.get_realtime_client, '_client'):
        delattr(gemini_client.get_realtime_client, '_client')


@pytest.mark.integration
@pytest.mark.usefixtures('dev_env')
def test_gemini_connection_dev() -> None:
    """
    Tests that the Gemini client can be created successfully in a dev environment.
    This is a basic check to ensure the API key and environment are set up correctly.
    """
    client = gemini_client.get_client()
    assert client is not None, 'Failed to create Gemini client.'


@pytest.mark.integration
@pytest.mark.usefixtures('dev_env')
def test_generate_gemini_content_dev() -> None:
    """
    Tests the content generation with a simple "Hello World" prompt in a dev environment.
    Ensures that the client can connect to the Gemini API and get a valid response.
    """
    # Given
    prompt = ['Hello! How are you?']

    # When
    response = gemini_client.generate_gemini_content(prompt)

    # Then
    print(f'Gemini Response: {response}')
    assert isinstance(response, str)
    assert len(response) > 0


@pytest.mark.integration
@pytest.mark.usefixtures('prod_env')
def test_vertex_ai_connection_prod() -> None:
    """
    Tests that the Vertex AI client can be created successfully in a prod environment.
    """
    client = gemini_client.get_client()
    assert client is not None, 'Failed to create Vertex AI client for production.'


@pytest.mark.integration
@pytest.mark.usefixtures('prod_env')
def test_generate_gemini_content_prod() -> None:
    """
    Tests the content generation with a simple "Hello World" prompt using Vertex AI.
    """
    # Given
    prompt = ['Hello Vertex AI! How are you?']

    # When
    response = gemini_client.generate_gemini_content(prompt)

    # Then
    print(f'Vertex AI Response: {response}')
    assert isinstance(response, str)
    assert len(response) > 0
