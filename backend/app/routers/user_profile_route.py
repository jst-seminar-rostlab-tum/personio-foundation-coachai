from typing import Annotated, Union
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session as DBSession

from app.database import get_db_session
from app.dependencies import require_admin, require_user
from app.models.user_profile import UserProfile
from app.schemas.user_profile import (
    UserProfileExtendedRead,
    UserProfileRead,
    UserProfileReplace,
    UserProfileUpdate,
    UserStatisticsRead,
)
from app.services.user_profile_service import UserService

router = APIRouter(prefix='/user-profile', tags=['User Profiles'])


def get_user_service(db: Annotated[DBSession, Depends(get_db_session)]) -> UserService:
    return UserService(db)


@router.get(
    '',
    response_model=Union[list[UserProfileRead], list[UserProfileExtendedRead]],
    dependencies=[Depends(require_admin)],
)
def get_user_profiles(
    service: Annotated[UserService, Depends(get_user_service)],
    detailed: bool = False,
) -> Union[list[UserProfileRead], list[UserProfileExtendedRead]]:
    """
    Retrieve all user profiles.

    - If `detailed` is False (default), returns simplified profiles.

    - If `detailed` is True, returns extended profiles including goals and confidence scores.
    """
    return service.get_user_profiles(detailed=detailed)


@router.get(
    '/profile',
    response_model=Union[UserProfileRead, UserProfileExtendedRead],
)
def get_user_profile(
    user_profile: Annotated[UserProfile, Depends(require_user)],
    service: Annotated[UserService, Depends(get_user_service)],
    detailed: bool = Query(False, description='Return extended profile details'),
) -> Union[UserProfileRead, UserProfileExtendedRead]:
    """
    Retrieve a single user profile.

    - If `detailed` is False (default), returns simplified profiles.

    - If `detailed` is True, returns extended profiles including goals and confidence scores.
    """
    return service.get_user_profile_by_id(user_id=user_profile.id, detailed=detailed)


@router.get('/stats', response_model=UserStatisticsRead)
def get_user_stats(
    user_profile: Annotated[UserProfile, Depends(require_user)],
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserStatisticsRead:
    return service.get_user_statistics(user_id=user_profile.id)


@router.put('', response_model=UserProfileExtendedRead)
def replace_user_profile(
    user_profile: Annotated[UserProfile, Depends(require_user)],
    data: UserProfileReplace,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserProfileExtendedRead:
    return service.replace_user_profile(
        user_id=user_profile.id,
        data=data,
    )


@router.patch('', response_model=UserProfileExtendedRead)
def update_user_profile(
    user_profile: Annotated[UserProfile, Depends(require_user)],
    data: UserProfileUpdate,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserProfileExtendedRead:
    return service.update_user_profile(
        user_id=user_profile.id,
        data=data,
    )


@router.delete('', response_model=dict)
def delete_user_profile(
    user_profile: Annotated[UserProfile, Depends(require_user)],
    service: Annotated[UserService, Depends(get_user_service)],
    delete_user_id: UUID | None = None,
) -> dict:
    """
    Delete a user profile by its unique user ID.
    Cascades the deletion to related goals and confidence scores.
    """
    return service.delete_user_profile(
        user_profile=user_profile,
        delete_user_id=delete_user_id,
    )
