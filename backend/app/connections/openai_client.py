"""External service clients for openai client."""

from __future__ import annotations

import os
from typing import TypeVar

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

from app.config import Settings

# Load environment variables from .env file
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')

# Load settings from the config.py
settings = Settings()
FORCE_CHEAP_MODEL = settings.FORCE_CHEAP_MODEL
DEFAULT_CHEAP_MODEL = 'gpt-4o-mini'


# Check for API key and handle edge cases
def _is_valid_api_key(key: str | None) -> bool:
    """Validate that the OpenAI API key is present and non-empty.

    Parameters:
        key (str | None): Candidate API key value.

    Returns:
        bool: True if the key is a non-empty string.
    """
    return bool(key and isinstance(key, str) and key.strip())


if not _is_valid_api_key(openai_api_key):
    print(
        '[WARNING] OPENAI_API_KEY is missing or invalid. '
        'AI features will be disabled and mock responses will be used.'
    )
    ENABLE_AI = False
    client = None
else:
    ENABLE_AI = settings.ENABLE_AI
    client = OpenAI(api_key=openai_api_key)


def get_client() -> OpenAI:
    """Return the configured OpenAI client instance.

    Returns:
        OpenAI: Configured OpenAI client.

    Raises:
        RuntimeError: If the client is not available or AI is disabled.
    """
    if not ENABLE_AI or client is None:
        raise RuntimeError(
            'OpenAI client is not available because ENABLE_AI is False or client is None.'
        )
    return client


# This is a type variable for the output model, which must be a subclass of BaseModel
T = TypeVar('T', bound=BaseModel)


def call_structured_llm(
    request_prompt: str,
    model: str,
    output_model: type[T],
    temperature: float = 1,
    max_tokens: int = 500,
    system_prompt: str | None = None,
    mock_response: T | None = None,
    audio_uri: str | None = None,
) -> T:
    """Call the LLM with a structured output request and parse the response.

    Parameters:
        request_prompt (str): User prompt content.
        model (str): Model name to use.
        output_model (type[T]): Pydantic model for structured parsing.
        temperature (float): Sampling temperature.
        max_tokens (int): Maximum output tokens.
        system_prompt (str | None): Optional system prompt.
        mock_response (T | None): Fallback response when AI is disabled.
        audio_uri (str | None): Optional audio input reference.

    Returns:
        T: Parsed structured response.

    Raises:
        ValueError: If AI is disabled without a mock response or parsing fails.
    """
    if not ENABLE_AI or client is None:
        if not mock_response:
            raise ValueError('AI is disabled and no mock response provided')
        return mock_response

    selected_model = DEFAULT_CHEAP_MODEL if FORCE_CHEAP_MODEL else (model or DEFAULT_CHEAP_MODEL)

    messages = []
    if system_prompt is not None:
        messages.append({'role': 'system', 'content': system_prompt})
    messages.append({'role': 'user', 'content': request_prompt})

    response = client.responses.parse(
        model=selected_model,
        input=messages,
        temperature=temperature,
        max_output_tokens=max_tokens,
        text_format=output_model,
    )

    if not response.output_parsed:
        raise ValueError('LLM did not return a valid response')

    return response.output_parsed
