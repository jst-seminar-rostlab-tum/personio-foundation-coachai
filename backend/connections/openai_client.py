from __future__ import annotations

import os
from typing import TypeVar, Callable, Any

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel
from backend.config import Settings

# Load environment variables from .env file
load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Load settings from the config.py
settings = Settings()
ENABLE_AI = settings.ENABLE_AI
FORCE_CHEAP_MODEL = settings.FORCE_CHEAP_MODEL
DEFAULT_CHEAP_MODEL = "gpt-4o-mini"


def get_client() -> OpenAI:
    """
    Returns the OpenAI client instance.

    returns:
    - OpenAI client instance
    """
    return client


# This is a type variable for the output model, which must be a subclass of BaseModel
T = TypeVar('T', bound=BaseModel)


def _call_structured_llm(
        request_prompt: str,
        model: str,
        output_model: type[T],
        temperature: float = 1,
        max_tokens: int = 500,
        system_prompt: str | None = None,
) -> T:
    """
    Call the LLM with a structured output request and parse the response.
    """
    messages = []
    if system_prompt is not None:
        messages.append({'role': 'system', 'content': system_prompt})
    messages.append({'role': 'user', 'content': request_prompt})

    response = client.responses.parse(
        model=model,
        input=messages,
        temperature=temperature,
        max_output_tokens=max_tokens,
        text_format=output_model,
    )

    if not response.output_parsed:
        raise ValueError('LLM did not return a valid response')

    return response.output_parsed


def call_ai_service(
        mock_response: Any = None,
        model: str = None,
        llm_function: Callable[..., Any] = None,
        function_args: dict = None,
):
    """
    General entry point for calling an AI service.

    Args:
        mock_response: The mock response to return when AI is disabled.
        model: The model name to use. If not specified, the default model is used.
        llm_function: The function that actually calls the LLM.
        function_args: Arguments to pass to llm_function.

    Returns:
        The response from the LLM, or mock_response if AI is disabled.
    """
    # Check if AI is enabled
    if not ENABLE_AI:
        return mock_response

    # If no model is specified, use the default cheap model
    final_model = DEFAULT_CHEAP_MODEL if FORCE_CHEAP_MODEL else (model or DEFAULT_CHEAP_MODEL)

    final_args = dict(function_args or {})
    if model is not None:
        final_args["model"] = final_model

    return llm_function(**final_args)
