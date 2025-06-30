import logging
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status
from gotrue import AdminUserAttributes, SignUpWithPasswordCredentials
from pydantic import BaseModel
from sqlmodel import Session as DBSession

from app.config import Settings
from app.database import get_db_session, get_supabase_client
from app.dependencies import JWTPayload, verify_jwt
from app.models.user_profile import UserProfile
from app.services.twilio_service import check_verification_code, send_verification_code

router = APIRouter(prefix='/auth', tags=['Auth'])

settings = Settings()


class CreateUserRequest(BaseModel):
    full_name: str
    phone: str
    email: str
    password: str
    # code: str


class SendVerificationRequest(BaseModel):
    phone_number: str


class VerifyCodeRequest(BaseModel):
    phone_number: str
    code: str


@router.post('/send-verification', response_model=None)
def send_verification(req: SendVerificationRequest) -> None:
    try:
        status = send_verification_code(req.phone_number)
        if status == 'failed':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Failed to send verification code',
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.post('/verify-code', response_model=None)
def verify_code(req: VerifyCodeRequest) -> None:
    try:
        status = check_verification_code(req.phone_number, req.code)
        if status != 'approved':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Invalid verification code',
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.post('', response_model=None, status_code=status.HTTP_201_CREATED)
def create_user(req: CreateUserRequest) -> None:
    try:
        CreateUserRequest.model_validate(req)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        ) from e

    try:
        supabase = get_supabase_client

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
    # try:
    #     supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
    #     # List all users with this email
    #     users = supabase.auth.admin.list_users(email=email)
    #     user = None
    #     for u in users['users']:
    #         if u['email'] == email:
    #             user = u
    #             break
    #     if not user:
    #         raise HTTPException(status_code=404, detail='User not found')
    #     # Check if user is confirmed (email_confirmed_at is not None)
    #     if user.get('email_confirmed_at'):
    #         raise HTTPException(status_code=400, detail='User already confirmed')
    #     # Delete user
    #     supabase.auth.admin.delete_user(user['id'])
    # except Exception as e:
    #     raise HTTPException(status_code=400, detail=f'Failed to delete user: {e}') from e
