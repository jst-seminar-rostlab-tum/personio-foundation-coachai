from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlmodel import Session as DBSession

from app.dependencies.auth import require_user
from app.dependencies.database import get_db_session
from app.dependencies.sessions import require_sessions_left_today
from app.models.user_profile import UserProfile
from app.schemas.session import SessionCreate, SessionDetailsRead, SessionRead, SessionUpdate
from app.schemas.sessions_paginated import PaginatedSessionRead
from app.services.session_service import SessionService

router = APIRouter(prefix='/sessions', tags=['Sessions'])


def get_session_service(
    db_session: Annotated[DBSession, Depends(get_db_session)],
) -> SessionService:
    """
    Dependency factory to inject the SessionService.
    """
    return SessionService(db_session)


@router.get('/{id}', response_model=SessionDetailsRead)
def get_session_by_id(
    id: UUID,
    user_profile: Annotated[UserProfile, Depends(require_user)],
    service: Annotated[SessionService, Depends(get_session_service)],
) -> SessionDetailsRead:
    """
    Retrieve a session by its ID.
    """
    return service.fetch_session_details(id, user_profile)


@router.get('', response_model=PaginatedSessionRead)
def get_sessions(
    user_profile: Annotated[UserProfile, Depends(require_user)],
    service: Annotated[SessionService, Depends(get_session_service)],
    scenario_id: UUID | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
) -> PaginatedSessionRead:
    """
    Return paginated list of completed sessions for a user.
    """
    return service.fetch_paginated_sessions(user_profile, page, page_size, scenario_id)


@router.post('', response_model=SessionRead, dependencies=[Depends(require_sessions_left_today)])
def create_session(
    session_data: SessionCreate,
    service: Annotated[SessionService, Depends(get_session_service)],
    user_profile: Annotated[UserProfile, Depends(require_user)],
) -> SessionRead:
    """
    Create a new session.
    """
    return service.create_new_session(session_data, user_profile)


@router.put('/{id}', response_model=SessionRead)
def update_session(
    id: UUID,
    updated_data: SessionUpdate,
    user_profile: Annotated[UserProfile, Depends(require_user)],
    background_tasks: BackgroundTasks,
    service: Annotated[SessionService, Depends(get_session_service)],
) -> SessionRead:
    """
    Update an existing session.
    """
    return service.update_existing_session(id, updated_data, user_profile, background_tasks)


@router.delete('/clear-all', response_model=dict)
def delete_sessions_by_user(
    user_profile: Annotated[UserProfile, Depends(require_user)],
    service: Annotated[SessionService, Depends(get_session_service)],
) -> dict:
    """
    Delete all sessions related to conversation scenarios for a given user ID.
    """
    return service.delete_all_user_sessions(user_profile)


@router.delete('/{id}', response_model=dict)
def delete_session(
    id: UUID,
    service: Annotated[SessionService, Depends(get_session_service)],
    user_profile: Annotated[UserProfile, Depends(require_user)],
) -> dict:
    """
    Delete a session.
    """
    return service.delete_session_by_id(id, user_profile)
