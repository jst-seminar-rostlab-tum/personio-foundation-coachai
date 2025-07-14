import logging
from datetime import UTC, datetime
from typing import Annotated, Any, NoReturn, TypedDict
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select

from app.config import Settings
from app.database import get_db_session
from app.models import UserProfile
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
    db: Annotated[Session, Depends(get_db_session)],
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

    _update_login_streak(db, user)

    return user


def require_admin(
    token: Annotated[JWTPayload, Depends(verify_jwt)],
    db: Annotated[Session, Depends(get_db_session)],
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

    _update_login_streak(db, user)

    return user


def _update_login_streak(db: Session, user_profile: UserProfile) -> None:
    # Check if the last_logged_in date is available
    if user_profile.last_logged_in:
        now = datetime.now(UTC)
        last_logged_in = user_profile.last_logged_in.replace(tzinfo=UTC)

        # Calculate the difference in days
        days_difference = (now - last_logged_in).days

        if days_difference == 1:
            # Increment streak if it's a new day
            user_profile.current_streak_days += 1
        elif days_difference > 1:
            # Reset streak if it's 2+ days later
            user_profile.current_streak_days = 0

        if days_difference != 0:
            # Update last_logged_in to the current time only if there is a streak increment or reset
            user_profile.last_logged_in = datetime.now(UTC)

            # Commit changes to the database
            db.add(user_profile)
            db.commit()
            db.refresh(user_profile)
