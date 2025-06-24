from collections.abc import Generator
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from app.services.user_profile_service import delete_supabase_user


@pytest.fixture
def mock_supabase() -> Generator[MagicMock, None, None]:
    with patch('app.services.user_profile_service.supabase') as mock:
        yield mock


def test_delete_supabase_user_success(mock_supabase: MagicMock) -> None:
    user_id = uuid4()

    delete_supabase_user(user_id)

    mock_supabase.auth.admin.delete_user.assert_called_once_with(str(user_id))
