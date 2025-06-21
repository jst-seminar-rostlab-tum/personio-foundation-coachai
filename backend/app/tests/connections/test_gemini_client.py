import pytest

from app.connections.gemini_client import generate_gemini_content, get_client


@pytest.fixture(autouse=True)
def enable_ai_for_tests(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Fixture to automatically enable AI for all tests in this module.
    """
    monkeypatch.setattr('app.connections.gemini_client.ENABLE_AI', True)


@pytest.mark.integration
def test_gemini_connection() -> None:
    """
    Tests that the Gemini client can be created successfully.
    This is a basic check to ensure the API key and environment are set up correctly.
    """
    client = get_client()
    assert client is not None, 'Failed to create Gemini client.'


@pytest.mark.integration
def test_generate_gemini_content() -> None:
    """
    Tests the content generation with a simple "Hello World" prompt.
    Ensures that the client can connect to the Gemini API and get a valid response.
    """
    # Given
    prompt = ['Hello! How are you?']

    # When
    response = generate_gemini_content(prompt)

    # Then
    print(f'Gemini Response: {response}')
    assert isinstance(response, str)
    assert len(response) > 0
