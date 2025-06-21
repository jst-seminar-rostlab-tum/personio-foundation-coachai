from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlmodel import Session as DBSession

from app.database import get_db_session
from app.dependencies import require_user
from app.models.user_profile import UserProfile
from app.schemas.session import SessionCreate, SessionDetailsRead, SessionRead, SessionUpdate
from app.schemas.sessions_paginated import PaginatedSessionsResponse
from app.services.session_service import SessionService

router = APIRouter(prefix='/session', tags=['Sessions'])


def get_session_service(
    db_session: Annotated[DBSession, Depends(get_db_session)],
) -> SessionService:
    """
    Dependency factory to inject the SessionService.
    """
    return SessionService(db_session)


@router.get('/{session_id}', response_model=SessionDetailsRead)
def get_session_by_id(
    session_id: UUID,
    user_profile: Annotated[UserProfile, Depends(require_user)],
    service: Annotated[SessionService, Depends(get_session_service)],
) -> SessionDetailsRead:
    """
    Retrieve a session by its ID.
    """
    return service.fetch_session_details(session_id, user_profile)


@router.get('', response_model=PaginatedSessionsResponse)
def get_sessions(
    user_profile: Annotated[UserProfile, Depends(require_user)],
    service: Annotated[SessionService, Depends(get_session_service)],
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
) -> PaginatedSessionsResponse:
    """
    Return paginated list of completed sessions for a user.
    """
    return service.fetch_paginated_sessions(user_profile, page, page_size)


@router.post('', response_model=SessionRead, dependencies=[Depends(require_user)])
def create_session(
    session_data: SessionCreate,
    service: Annotated[SessionService, Depends(get_session_service)],
) -> SessionRead:
    """
    Create a new session.
    """
    return service.create_new_session(session_data)


@router.put('/{session_id}', response_model=SessionRead)
def update_session(
    session_id: UUID,
    updated_data: SessionUpdate,
    user_profile: Annotated[UserProfile, Depends(require_user)],
    background_tasks: BackgroundTasks,
    service: Annotated[SessionService, Depends(get_session_service)],
) -> SessionRead:
    """
    Update an existing session.
    """
    return service.update_existing_session(session_id, updated_data, user_profile, background_tasks)


@router.delete('/clear-all', response_model=dict)
def delete_sessions_by_user(
    user_profile: Annotated[UserProfile, Depends(require_user)],
    service: Annotated[SessionService, Depends(get_session_service)],
) -> dict:
    """
    Delete all sessions related to conversation scenarios for a given user ID.
    """
    return service.delete_all_user_sessions(user_profile)


@router.delete('/{session_id}', response_model=dict)
def delete_session(
    session_id: UUID,
    service: Annotated[SessionService, Depends(get_session_service)],
    user_profile: Annotated[UserProfile, Depends(require_user)],
) -> dict:
    """
    Delete a session.
    """
    return service.delete_session_by_id(session_id, user_profile)
