from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlmodel import Session as DBSession
from sqlmodel import select

from app.dependencies.auth import require_user
from app.dependencies.database import get_db_session
from app.enums.account_role import AccountRole
from app.enums.session_status import SessionStatus
from app.models.session import Session
from app.models.user_profile import UserProfile
from app.services.app_config_service import AppConfigService, get_app_config_service


def require_session_access(
    session_id: UUID,
    db_session: Annotated[DBSession, Depends(get_db_session)],
    user_profile: Annotated[UserProfile, Depends(require_user)],
) -> Session:
    session = db_session.exec(select(Session).where(Session.id == session_id)).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Session not found',
        )
    if session.scenario.user_id != user_profile.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='User is not the owner of the scenario',
        )
    if session.status is SessionStatus.completed:
        raise HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS, detail='Session is already completed'
        )
    return session


def require_sessions_left_today(
    user_profile: Annotated[UserProfile, Depends(require_user)],
    app_config_service: Annotated[AppConfigService, Depends(get_app_config_service)],
) -> None:
    if user_profile.account_role == AccountRole.admin:
        return

    daily_session_limit = user_profile.daily_session_limit
    if daily_session_limit is None:
        daily_session_limit = app_config_service.get_default_daily_session_limit()

    if daily_session_limit is None or user_profile.sessions_created_today >= daily_session_limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail='You have reached the daily session limit. Cannot start a real-time session.',
        )
