from __future__ import annotations

import os
from typing import TypeVar

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

from app.config import Settings

# Load environment variables from .env file
load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Load settings from the config.py
settings = Settings()
ENABLE_AI = settings.ENABLE_AI
FORCE_CHEAP_MODEL = settings.FORCE_CHEAP_MODEL
DEFAULT_CHEAP_MODEL = 'gpt-4o-mini'


def get_client() -> OpenAI:
    """
    Returns the OpenAI client instance.

    returns:
    - OpenAI client instance
    """
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
) -> T:
    """
    Call the LLM with a structured output request and parse the response.
    """
    if not ENABLE_AI:
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
