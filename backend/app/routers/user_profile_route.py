from typing import Annotated, Optional, Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session as DBSession

from app.database import get_db_session
from app.dependencies import require_user
from app.models.user_profile import (
    UserProfile,
    UserProfileExtendedRead,
    UserProfileRead,
    UserProfileReplace,
    UserProfileUpdate,
)
from app.services.user_profile_service import UserProfileService

router = APIRouter(prefix='/user-profile', tags=['User Profiles'])


def get_user_profile_service(
    db_session: Annotated[DBSession, Depends(get_db_session)],
) -> UserProfileService:
    return UserProfileService(db_session)


@router.get(
    '',
    response_model=Union[list[UserProfileRead], list[UserProfileExtendedRead]],
)
def get_user_profiles(
    service: Annotated[UserProfileService, Depends(get_user_profile_service)],
    detailed: Annotated[bool, Query(description='...')] = False,
) -> Union[list[UserProfileRead], list[UserProfileExtendedRead]]:
    """
    Retrieve all user profiles.
    - `detailed=False` → simple profiles

    - `detailed=True` → profiles + goals + confidence scores
    """
    return service.get_profiles(detailed)


@router.get(
    '/profile',
    response_model=Union[UserProfileRead, UserProfileExtendedRead],
)
def get_user_profile(
    user_profile: Annotated[UserProfile, Depends(require_user)],
    service: Annotated[UserProfileService, Depends(get_user_profile_service)],
    detailed: Annotated[bool, Query(description='...')] = False,
) -> Union[UserProfileRead, UserProfileExtendedRead]:
    """
    Retrieve a single user profile.
    """
    return service.get_profile(user_profile.id, detailed)


@router.put(
    '',
    response_model=UserProfileExtendedRead,
)
def replace_user_profile(
    user_profile: Annotated[UserProfile, Depends(require_user)],
    data: UserProfileReplace,
    service: Annotated[UserProfileService, Depends(get_user_profile_service)],
) -> UserProfileExtendedRead:
    """
    Fully replace a user profile (PUT).
    """
    return service.replace_profile(user_profile.id, data)


@router.patch(
    '',
    response_model=UserProfileExtendedRead,
)
def update_user_profile(
    user_profile: Annotated[UserProfile, Depends(require_user)],
    data: UserProfileUpdate,
    service: Annotated[UserProfileService, Depends(get_user_profile_service)],
) -> UserProfileExtendedRead:
    """
    Partially update a user profile (PATCH).
    """
    return service.update_profile(user_profile.id, data)


@router.delete(
    '',
    response_model=dict,
)
def delete_user_profile(
    user_profile: Annotated[UserProfile, Depends(require_user)],
    service: Annotated[UserProfileService, Depends(get_user_profile_service)],
    delete_user_id: Annotated[
        Optional[UUID], Query(description='User ID to delete (admin only)')
    ] = None,
) -> dict[str, str]:
    """
    Delete a user profile.
    - Admins can delete other users via `delete_user_id`
    - Normal users can only delete themselves
    """
    # Admin override logic
    if delete_user_id and user_profile.account_role == 'admin':
        user_id = delete_user_id
    elif delete_user_id and delete_user_id != user_profile.id:
        raise HTTPException(403, 'Admin access required to delete other users')
    else:
        user_id = user_profile.id

    return service.delete_profile(user_id)
