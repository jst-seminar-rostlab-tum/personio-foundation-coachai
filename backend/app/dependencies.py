import logging
from typing import Annotated, Any, TypedDict

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


def verify_jwt(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> JWTPayload:
    """
    Checks the validity of the JWT token and retrieves its information.
    """
    logging.info('Verifying JWT')
    if settings.stage == 'dev' and settings.DEV_MODE_SKIP_AUTH:
        return {'sub': str(settings.DEV_MODE_MOCK_USER_ID)}

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
    Checks if the user is authenticated and has the role of 'user' or 'admin'.
    """
    user_id = token['sub']
    statement = select(UserProfile).where(UserProfile.id == user_id)
    user = db.exec(statement).first()
    if not user or user.account_role not in [AccountRole.user, AccountRole.admin]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail='User does not have access'
        )
    return user


def require_admin(
    token: Annotated[JWTPayload, Depends(verify_jwt)],
    db: Annotated[Session, Depends(get_db_session)],
) -> UserProfile:
    """
    Checks if the user is authenticated and has the role of 'admin'.
    """
    user_id = token['sub']
    statement = select(UserProfile).where(UserProfile.id == user_id)
    user = db.exec(statement).first()
    if not user or user.account_role != AccountRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Admin access required')
    return user
