from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException
from pytest_mock import MockerFixture

from app.models.user_profile import UserProfile
from app.services.user_profile_service import UserService


@pytest.fixture
def mock_user() -> UserProfile:
    return UserProfile(
        id=uuid4(), full_name='Test User', email='testuser@example.com', phone_number='1234567890'
    )


@pytest.fixture
def mock_db(mock_user: UserProfile) -> MagicMock:
    db = MagicMock()
    db.get.return_value = mock_user
    return db


@pytest.fixture
def user_service(mock_db: MagicMock) -> UserService:
    return UserService(db=mock_db)


@pytest.fixture
def mock_supabase(mocker: MockerFixture) -> MagicMock:
    mock_client = MagicMock()
    mocker.patch('app.services.user_profile_service.get_supabase_client', return_value=mock_client)
    return mock_client


def test__delete_user_success(
    user_service: UserService, mock_user: UserProfile, mock_db: MagicMock, mock_supabase: MagicMock
) -> None:
    user_service._delete_user(mock_user.id)

    mock_db.get.assert_called_once_with(UserProfile, mock_user.id)
    mock_db.delete.assert_called_once_with(mock_user)
    # mock_db.commit.assert_called_once()
    mock_supabase.auth.admin.delete_user.assert_called_once_with(str(mock_user.id))


def test__delete_user_db_commit_fails(
    user_service: UserService,
    mock_user: UserProfile,
    mock_db: MagicMock,
    mock_supabase: MagicMock,
) -> None:
    mock_db.commit.side_effect = Exception('DB error')

    with pytest.raises(HTTPException) as exc_info:
        user_service._delete_user(mock_user.id)

    # mock_db.rollback.assert_called_once()
    mock_supabase.auth.admin.delete_user.assert_not_called()
    assert exc_info.value.status_code == 500
