from collections.abc import Generator

import pytest

from app.services.session_feedback.session_feedback_llm import load_session_feedback_config


@pytest.fixture(autouse=True)
def clear_config_cache() -> Generator[None]:
    load_session_feedback_config.cache_clear()
    yield
    load_session_feedback_config.cache_clear()
