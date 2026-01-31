import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlmodel import Session as DBSession
from supabase_auth import (
    SignUpWithPasswordCredentials,
)

from app.config import Settings
from app.dependencies.database import get_db_session, get_supabase_client
from app.models.user_profile import UserProfile
from app.schemas.auth import (
    CheckUniqueRequest,
    UserCreate,
    VerificationCodeCreate,
)
from app.services.twilio_service import check_verification_code, send_verification_code

router = APIRouter(prefix='/auth', tags=['Auth'])

settings = Settings()


@router.post('/send-phone-verification-code', response_model=None)
def send_verification(req: VerificationCodeCreate) -> None:
    verification_status = send_verification_code(req.phone_number)
    if verification_status == 'failed':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Failed to send verification code',
        )


@router.post('/sign-up-user', response_model=None)
def sign_up_user(
    req: UserCreate,
    db_session: Annotated[DBSession, Depends(get_db_session)],
) -> None:
    verification_status = check_verification_code(req.phone, req.verification_code)
    if verification_status != 'approved':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid verification code',
        )

    try:
        supabase = get_supabase_client()

        credentials: SignUpWithPasswordCredentials = {
            'email': req.email,
            'password': req.password,
        }

        user_response = supabase.auth.sign_up(credentials)

        user_data = UserProfile(
            id=user_response.user.id,
            full_name=req.full_name,
            email=user_response.user.email,
            phone_number=req.phone,
            organization_name=req.organization_name,
        )

        db_session.add(user_data)
        db_session.commit()

    except Exception as e:
        logging.warning('Unhandled exception when creating user: ', e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.post('/check-unique', status_code=status.HTTP_200_OK)
def check_unique(
    req: CheckUniqueRequest, db_session: Annotated[DBSession, Depends(get_db_session)]
) -> dict:
    # Remove '+' from phone number for database comparison
    phone_for_db = req.phone.lstrip('+')

    # Check UserProfile table
    email_exists_db = (
        db_session.exec(select(UserProfile).where(UserProfile.email == req.email)).first()
        is not None
    )
    phone_exists_db = (
        db_session.exec(select(UserProfile).where(UserProfile.phone_number == phone_for_db)).first()
        is not None
    )

    # Check Supabase Auth
    supabase = get_supabase_client()
    users = supabase.auth.admin.list_users()
    email_exists_auth = any(getattr(u, 'email', None) == req.email for u in users)
    phone_exists_auth = any(getattr(u, 'phone', None) == req.phone for u in users)

    return {
        'emailExists': email_exists_db or email_exists_auth,
        'phoneExists': phone_exists_db or phone_exists_auth,
    }
