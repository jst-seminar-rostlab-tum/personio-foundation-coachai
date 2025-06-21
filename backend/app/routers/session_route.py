from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlmodel import Session as DBSession

from app.database import get_db_session
from app.dependencies import require_user
from app.models.user_profile import UserProfile
from app.schemas.session import SessionCreate, SessionDetailsRead, SessionRead, SessionUpdate
from app.schemas.sessions_paginated import PaginatedSessionsResponse
from app.services.session_service import (
    create_new_session,
    delete_all_user_sessions,
    delete_session_by_id,
    fetch_paginated_sessions,
    fetch_session_details,
    update_existing_session,
)

router = APIRouter(prefix='/session', tags=['Sessions'])


@router.get('/{session_id}', response_model=SessionDetailsRead)
def get_session_by_id(
    session_id: UUID,
    db_session: Annotated[DBSession, Depends(get_db_session)],
    user_profile: Annotated[UserProfile, Depends(require_user)],
) -> SessionDetailsRead:
    """
    Retrieve a session by its ID.
    """
    return fetch_session_details(session_id, db_session, user_profile)


@router.get('', response_model=PaginatedSessionsResponse)
def get_sessions(
    user_profile: Annotated[UserProfile, Depends(require_user)],
    db_session: Annotated[DBSession, Depends(get_db_session)],
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
) -> PaginatedSessionsResponse:
    """
    Return paginated list of completed sessions for a user.
    """
    return fetch_paginated_sessions(user_profile, db_session, page, page_size)


@router.post('', response_model=SessionRead, dependencies=[Depends(require_user)])
def create_session(
    session_data: SessionCreate, db_session: Annotated[DBSession, Depends(get_db_session)]
) -> SessionRead:
    """
    Create a new session.
    """
    return create_new_session(session_data, db_session)


@router.put('/{session_id}', response_model=SessionRead)
def update_session(
    session_id: UUID,
    updated_data: SessionUpdate,
    db_session: Annotated[DBSession, Depends(get_db_session)],
    background_tasks: BackgroundTasks,
    user_profile: Annotated[UserProfile, Depends(require_user)],
) -> SessionRead:
    """
    Update an existing session.
    """
    return update_existing_session(
        session_id, updated_data, db_session, background_tasks, user_profile
    )


@router.delete('/clear-all', response_model=dict)
def delete_sessions_by_user(
    db_session: Annotated[DBSession, Depends(get_db_session)],
    user_profile: Annotated[UserProfile, Depends(require_user)],
) -> dict:
    """
    Delete all sessions related to conversation scenarios for a given user ID.
    """
    return delete_all_user_sessions(db_session, user_profile)


@router.delete('/{session_id}', response_model=dict)
def delete_session(
    session_id: UUID,
    db_session: Annotated[DBSession, Depends(get_db_session)],
    user_profile: Annotated[UserProfile, Depends(require_user)],
) -> dict:
    """
    Delete a session.
    """
    return delete_session_by_id(session_id, db_session, user_profile)
