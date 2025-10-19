import io
import json
import zipfile
from typing import Annotated, Union
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlmodel import Session as DBSession
from sqlmodel import select

from app.connections.gcs_client import get_gcs_audio_manager
from app.database import get_db_session
from app.dependencies import require_admin, require_user
from app.models.conversation_scenario import ConversationScenario
from app.models.user_profile import UserProfile
from app.schemas.user_profile import (
    UserDailySessionLimitUpdate,
    UserListPaginatedRead,
    UserProfileExtendedRead,
    UserProfileRead,
    UserProfileReplace,
    UserProfileUpdate,
    UserStatistics,
)
from app.services.user_export_service import _collect_audio_files_for_export, build_user_data_export
from app.services.user_profile_service import UserService

router = APIRouter(prefix='/user-profiles', tags=['User Profiles'])


def get_user_service(db: Annotated[DBSession, Depends(get_db_session)]) -> UserService:
    return UserService(db)


@router.get(
    '',
    response_model=UserListPaginatedRead,
    dependencies=[Depends(require_admin)],
)
def get_user_profiles(
    requesting_user: Annotated[UserProfile, Depends(require_admin)],
    service: Annotated[UserService, Depends(get_user_service)],
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    email_substring: str | None = Query(
        None,
        description='Filter profiles by email substring',
        min_length=1,
        max_length=100,
    ),
) -> UserListPaginatedRead:
    """
    Retrieve all user profiles.
    """
    return service.get_user_profiles(
        requesting_user_id=requesting_user.id,
        page=page,
        limit=limit,
        email_substring=email_substring,
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


@router.get('/stats', response_model=UserStatistics)
def get_user_stats(
    user_profile: Annotated[UserProfile, Depends(require_user)],
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserStatistics:
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

    # Build the export data
    export_data = build_user_data_export(user_profile, db_session)
    json_bytes = json.dumps(export_data.dict(), indent=2).encode('utf-8')

    # Get sessions to collect audio files
    scenarios = db_session.exec(
        select(ConversationScenario).where(ConversationScenario.user_id == user_profile.id)
    ).all()

    sessions = []
    for scenario in scenarios:
        for sess in scenario.sessions:
            sessions.append(sess)

    # Collect audio files organized by session
    audio_files_by_session = _collect_audio_files_for_export(sessions)

    # Create the zip file
    mem_zip = io.BytesIO()
    with zipfile.ZipFile(mem_zip, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
        # Add the JSON data
        zf.writestr('user_data_export.json', json_bytes)

        # Add audio files organized by session
        gcs_manager = get_gcs_audio_manager()
        if gcs_manager and audio_files_by_session:
            for session_id, audio_files in audio_files_by_session.items():
                for audio_uri, filename in audio_files:
                    try:
                        # Download audio file from GCS
                        audio_buffer = gcs_manager.download_to_bytesio(audio_uri)

                        # Add to zip in session folder
                        zip_path = f'audio/session_{session_id}/{filename}'
                        zf.writestr(zip_path, audio_buffer.getvalue())
                        audio_buffer.close()
                        print(f'Added audio file to export: {zip_path}')
                    except FileNotFoundError:
                        print(f'Audio file not found in GCS: {audio_uri}')
                    except Exception as e:
                        # Log error but continue with other files
                        print(f'Failed to download audio file {audio_uri}: {e}')
        else:
            print('No GCS manager available or no audio files found')

    mem_zip.seek(0)
    headers = {'Content-Disposition': 'attachment; filename="user_data_export.zip"'}
    return StreamingResponse(mem_zip, media_type='application/zip', headers=headers)


@router.patch(
    '/{user_id}/daily-session-limit',
    response_model=UserProfileRead,
    dependencies=[Depends(require_admin)],
)
def update_daily_session_limit(
    user_id: UUID,
    data: UserDailySessionLimitUpdate,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserProfileRead:
    return service.update_daily_session_limit(
        user_id=user_id, daily_session_limit=data.daily_session_limit
    )


@router.get('/{user_id}', response_model=UserProfileRead, dependencies=[Depends(require_admin)])
def get_user_profile_by_id(
    user_id: UUID,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserProfileRead:
    return service.get_user_profile_by_id(user_id=user_id, detailed=False)
