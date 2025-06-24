from unittest.mock import Mock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlmodel import Session

from app.models.language import LanguageCode
from app.models.user_profile import (
    AccountRole,
    Experience,
    PreferredLearningStyle,
    ProfessionalRole,
    UserProfile,
)
from app.routers.user_profile_route import delete_user


@pytest.fixture
def regular_user() -> UserProfile:
    return UserProfile(
        id=uuid4(),
        full_name='Regular User',
        email='user@example.com',
        phone_number='1234567890',
        preferred_language_code=LanguageCode.en,
        experience=Experience.beginner,
        preferred_learning_style=PreferredLearningStyle.visual,
        account_role=AccountRole.user,
        professional_role=ProfessionalRole.hr_professional,
    )


@pytest.fixture
def admin_user() -> UserProfile:
    return UserProfile(
        id=uuid4(),
        full_name='Admin User',
        email='admin@example.com',
        phone_number='0987654321',
        preferred_language_code=LanguageCode.en,
        experience=Experience.expert,
        preferred_learning_style=PreferredLearningStyle.auditory,
        account_role=AccountRole.admin,
        professional_role=ProfessionalRole.executive,
    )


@patch('app.routers.user_profile_route.delete_supabase_user')
@patch('app.routers.user_profile_route.delete_user_profile')
def test_user_can_self_delete(
    mock_delete_user_profile: None,
    mock_delete_supabase_user: None,
    regular_user: UserProfile,
) -> None:
    mock_db = Mock(spec=Session)

    delete_user(user_profile=regular_user, db_session=mock_db, delete_user_id=None)

    mock_delete_user_profile.assert_called_once_with(regular_user.id, mock_db)
    mock_delete_supabase_user.assert_called_once_with(regular_user.id)


@patch('app.routers.user_profile_route.delete_supabase_user')
@patch('app.routers.user_profile_route.delete_user_profile')
def test_regular_user_can_not_delete_another_user(
    mock_delete_user_profile: None,
    mock_delete_supabase_user: None,
    regular_user: UserProfile,
) -> None:
    mock_db = Mock(spec=Session)

    with pytest.raises(HTTPException) as exc_info:
        delete_user(
            user_profile=regular_user,
            db_session=mock_db,
            delete_user_id=uuid4(),
        )

    assert exc_info.value.status_code == 403
    mock_delete_user_profile.assert_not_called()
    mock_delete_supabase_user.assert_not_called()


@patch('app.routers.user_profile_route.delete_supabase_user')
@patch('app.routers.user_profile_route.delete_user_profile')
def test_admin_user_can_delete_other_user(
    mock_delete_user_profile: None,
    mock_delete_supabase_user: None,
    admin_user: UserProfile,
    regular_user: UserProfile,
) -> None:
    mock_db = Mock(spec=Session)

    delete_user(
        user_profile=admin_user,
        db_session=mock_db,
        delete_user_id=regular_user.id,
    )

    mock_delete_user_profile.assert_called_once_with(regular_user.id, mock_db)
    mock_delete_supabase_user.assert_called_once_with(regular_user.id)
