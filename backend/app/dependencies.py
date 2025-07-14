import logging
from datetime import datetime
from typing import Annotated, Any, NoReturn, TypedDict
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pytz import UTC
from pytz import timezone as pytz_timezone
from sqlmodel import Session as DBSession
from sqlmodel import select

from app.config import Settings
from app.database import get_db_session
from app.enums.session_status import SessionStatus
from app.models import Session, UserProfile
from app.models.user_profile import AccountRole

settings = Settings()
security = HTTPBearer(auto_error=not (settings.stage == 'dev' and settings.DEV_MODE_SKIP_AUTH))


class JWTPayload(TypedDict, total=False):
    iss: str
    sub: str
    aud: str
    exp: int
    iat: int
    email: str
    phone: str
    app_metadata: dict[str, Any]
    user_metadata: dict[str, Any]
    role: str
    aal: str
    amr: list[Any]
    session_id: str
    is_anonymous: bool


ALLOWED_ROLES = {AccountRole.user.value, AccountRole.admin.value}


def _forbidden(detail: str, log_msg: str, *args: str) -> NoReturn:
    """Log a warning and raise a 403 HttpException."""
    logging.warning(log_msg, *args)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


def verify_jwt(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> JWTPayload:
    """
    Checks the validity of the JWT token and retrieves its information.
    """
    if settings.stage == 'dev' and settings.DEV_MODE_SKIP_AUTH:
        logging.info('Skipping JWT verification')
        return JWTPayload(sub=str(settings.DEV_MODE_MOCK_ADMIN_ID))
    logging.info('Verifying JWT')
    if not credentials:
        logging.info('No JWT token')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication required'
        )

    token = credentials.credentials
    try:
        payload = jwt.decode(
            token, settings.SUPABASE_JWT_SECRET, algorithms=['HS256'], audience='authenticated'
        )
        return payload
    except jwt.ExpiredSignatureError as err:
        logging.info('JWT token expired')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Token has expired'
        ) from err
    except jwt.InvalidTokenError as err:
        logging.info('JWT token invalid')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token'
        ) from err
    except Exception as e:
        logging.warning('Unhandled exception during JWT token verification: ', e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Internal server error'
        ) from e


def require_user(
    token: Annotated[JWTPayload, Depends(verify_jwt)],
    db: Annotated[DBSession, Depends(get_db_session)],
    request: Request,
) -> UserProfile:
    """
    Checks that the JWT has a 'sub', that a UserProfile exists for it,
    and that its role is either 'user' or 'admin'.
    """
    user_id = token.get('sub') or _forbidden('Cannot find user', 'JWT payload missing "sub" claim')

    user = db.exec(
        select(UserProfile).where(UserProfile.id == UUID(user_id))
    ).first() or _forbidden('Cannot find user', 'User not found for ID %s', user_id)

    if user.account_role.value not in ALLOWED_ROLES:
        _forbidden(
            'User does not have access',
            'User role %s not in allowed roles %s',
            user.account_role,
            *ALLOWED_ROLES,
        )
    timezone = request.state.timezone

    _update_login_streak(db, user, timezone)

    return user


def require_admin(
    token: Annotated[JWTPayload, Depends(verify_jwt)],
    db: Annotated[DBSession, Depends(get_db_session)],
    request: Request,
) -> UserProfile:
    """
    Ensures the JWT has a 'sub' claim, the user exists, and is an admin.
    """
    user_id = token.get('sub') or _forbidden('Cannot find user', 'JWT payload missing "sub" claim')

    user = db.exec(
        select(UserProfile).where(UserProfile.id == UUID(user_id))
    ).first() or _forbidden('Cannot find user', 'User not found for ID %s', user_id)

    if user.account_role is not AccountRole.admin:
        _forbidden('Admin access required', 'User role %s is not admin', user.account_role.value)
    timezone = request.state.timezone
    _update_login_streak(db, user, timezone)

    return user


def _update_login_streak(db: DBSession, user_profile: UserProfile, timezone: str) -> None:
    """
    Updates the login streak for a user based on their last login time and the current time in the
    specified timezone.

    The function checks the difference in days between the user's last login time and the current
      time in the provided timezone.
    If the difference is exactly 1 day, the user's streak is incremented. If the difference is
      greater than 1 day, the streak is reset.
    The last login time is updated only if the streak is incremented or reset.

    Args:
        db (Session): The database session used to commit changes to the user profile.
        user_profile (UserProfile): The user profile object containing login streak information.
        timezone (str): The timezone string (e.g., "America/New_York") used to calculate the current
          time.

    Returns:
        None: This function does not return anything. It updates the user profile in the database.

    Notes:
        - The last login time is stored in UTC for consistency across the database.
        - The streak is calculated based on calendar days in the user's timezone.
    """
    # Check if the last_logged_in date is available
    if user_profile.last_logged_in:
        user_timezone = pytz_timezone(timezone)
        now = datetime.now(user_timezone)

        last_logged_in = user_profile.last_logged_in.astimezone(user_timezone)
        days_difference = (now.date() - last_logged_in.date()).days

        if days_difference == 1:
            user_profile.current_streak_days += 1
        elif days_difference > 1:
            user_profile.current_streak_days = 0

        if days_difference != 0:
            user_profile.last_logged_in = datetime.now(UTC)  # Store in UTC for consistency

            # Commit changes to the database
            db.add(user_profile)
            db.commit()
            db.refresh(user_profile)

    # Reset daily session counter if it's a new day
    today = datetime.now(UTC).date()
    if user_profile.last_session_date != today:
        user_profile.sessions_created_today = 0
        user_profile.last_session_date = today
        db.add(user_profile)
        db.commit()
        db.refresh(user_profile)


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
    if not session.scenario.user_id == user_profile.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='User is not the owner of the scenario',
        )
    if session.status is SessionStatus.completed:
        raise HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS, detail='Session is already completed'
        )
    return session
