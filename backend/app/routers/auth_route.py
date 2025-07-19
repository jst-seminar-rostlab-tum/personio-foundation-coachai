import logging
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status
from gotrue import AdminUserAttributes, SignUpWithPasswordCredentials
from sqlalchemy import select
from sqlmodel import Session as DBSession

from app.config import Settings
from app.database import get_db_session, get_supabase_client
from app.dependencies import JWTPayload, verify_jwt
from app.models.user_profile import UserProfile
from app.schemas.auth import (
    CheckUniqueRequest,
    UserCreate,
    VerificationCodeConfirm,
    VerificationCodeCreate,
)
from app.services.twilio_service import check_verification_code, send_verification_code

router = APIRouter(prefix='/auth', tags=['Auth'])

settings = Settings()


@router.post('/send-verification', response_model=None)
def send_verification(req: VerificationCodeCreate) -> None:
    verification_status = send_verification_code(req.phone_number)
    if verification_status == 'pending':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Failed to send verification code',
        )


@router.post('/verify-code', response_model=None)
def verify_code(req: VerificationCodeConfirm) -> None:
    verification_status = check_verification_code(req.phone_number, req.code)
    if verification_status != 'approved':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid verification code',
        )


@router.post('', response_model=None, status_code=status.HTTP_201_CREATED)
def create_user(req: UserCreate) -> None:
    try:
        UserCreate.model_validate(req)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        ) from e

    try:
        supabase = get_supabase_client()

        attributes: AdminUserAttributes = {
            'email': req.email,
            'password': req.password,
            'phone': req.phone,
            'phone_confirm': True,
            'user_metadata': {
                'full_name': req.full_name,
            },
        }
        supabase.auth.admin.create_user(attributes)

        credentials: SignUpWithPasswordCredentials = {
            'email': req.email,
            'password': req.password,
        }
        supabase.auth.sign_up(credentials)
    except Exception as e:
        logging.warning('Unhandled exception when creating user: ', e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get('/confirm', response_model=None)
def confirm_user(
    token: Annotated[JWTPayload, Depends(verify_jwt)],
    db_session: Annotated[DBSession, Depends(get_db_session)],
) -> None:
    if not token['user_metadata'].get('email_verified', False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User is not confirmed',
        )

    user_data = UserProfile(
        id=token['sub'],
        full_name=token['user_metadata']['full_name'],
        email=token['email'],
        phone_number=token['phone'],
    )
    db_session.add(user_data)
    db_session.commit()


@router.post('/delete-unconfirmed', response_model=None, status_code=status.HTTP_200_OK)
def delete_unconfirmed_user(email: str = Body(..., embed=True)) -> None:
    """
    Delete a user from Supabase Auth by email if not confirmed.
    """
    try:
        supabase = get_supabase_client()
        users = supabase.auth.admin.list_users()
        user = None
        for u in users:
            if getattr(u, 'email', None) == email:
                user = u
                break
        if not user:
            raise HTTPException(status_code=404, detail='User not found')
        supabase.auth.admin.delete_user(user.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f'Failed to delete user: {e}') from e


@router.post('/check-unique', status_code=200)
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
