import io
import json
import zipfile
from typing import Annotated, Union
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlmodel import Session as DBSession

from app.database import get_db_session
from app.dependencies import require_admin, require_user
from app.models.user_profile import UserProfile
from app.schemas.user_profile import (
    PaginatedUserResponse,
    UserProfileExtendedRead,
    UserProfileRead,
    UserProfileReplace,
    UserProfileUpdate,
    UserStatisticsRead,
)
from app.services.user_export_service import build_user_data_export
from app.services.user_profile_service import UserService

router = APIRouter(prefix='/user-profiles', tags=['User Profiles'])


def get_user_service(db: Annotated[DBSession, Depends(get_db_session)]) -> UserService:
    return UserService(db)


@router.get(
    '',
    response_model=PaginatedUserResponse,
    dependencies=[Depends(require_admin)],
)
def get_user_profiles(
    service: Annotated[UserService, Depends(get_user_service)],
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    email_substring: str | None = Query(
        None,
        description='Filter profiles by email substring',
        min_length=1,
        max_length=100,
    ),
) -> PaginatedUserResponse:
    """
    Retrieve all user profiles.
    """
    return service.get_user_profiles(
        page=page, page_size=page_size, email_substring=email_substring
    )


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
        user=user_profile,
        data=data,
    )


@router.patch('', response_model=UserProfileExtendedRead)
def update_user_profile(
    user_profile: Annotated[UserProfile, Depends(require_user)],
    data: UserProfileUpdate,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserProfileExtendedRead:
    return service.update_user_profile(
        user=user_profile,
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


@router.get('/export')
def export_user_data(
    user_profile: Annotated[UserProfile, Depends(require_user)],
    db_session: Annotated[DBSession, Depends(get_db_session)],
) -> StreamingResponse:
    """
    Export all user-related data (history) for the currently authenticated user as a zip file.
    """
    export_data = build_user_data_export(user_profile, db_session)
    json_bytes = json.dumps(export_data.dict(), indent=2).encode('utf-8')
    mem_zip = io.BytesIO()
    with zipfile.ZipFile(mem_zip, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('user_data_export.json', json_bytes)
    mem_zip.seek(0)
    headers = {'Content-Disposition': 'attachment; filename="user_data_export.zip"'}
    return StreamingResponse(mem_zip, media_type='application/zip', headers=headers)
