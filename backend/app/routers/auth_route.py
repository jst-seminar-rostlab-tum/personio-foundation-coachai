from fastapi import APIRouter, HTTPException, status
from gotrue import (
    SignInWithPasswordCredentials,
    SignUpWithPasswordCredentials,
)
from pydantic import BaseModel
from supabase import create_client

from app.config import Settings

router = APIRouter(prefix='/auth', tags=['Auth'])

settings = Settings()
supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)


class CreateUserRequest(BaseModel):
    full_name: str
    phone: str
    email: str
    password: str
    code: str


class LoginUserRequest(BaseModel):
    phone: str
    password: str


@router.post('/', response_model=None, status_code=status.HTTP_201_CREATED)
def create_user(req: CreateUserRequest) -> None:
    try:
        CreateUserRequest.model_validate(req)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        ) from e

    # TODO: Verify OTP code

    credentials: SignUpWithPasswordCredentials = {
        'email': req.email,
        'password': req.password,
        'options': {
            'data': {
                'full_name': req.full_name,
            }
        },
    }
    try:
        response = supabase.auth.sign_up(credentials)
        response = supabase.auth.admin.update_user_by_id(
            response.user.id,
            {
                'phone': req.phone,
                'phone_confirm': True,
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

    return 'User created successfully'


# TODO: Only for testing purposes, remove later
@router.post('/login', response_model=dict, status_code=status.HTTP_200_OK)
def login_user(req: LoginUserRequest) -> None:
    try:
        LoginUserRequest.model_validate(req)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        ) from e

    credentials: SignInWithPasswordCredentials = {
        'phone': req.phone,
        'password': req.password,
    }
    try:
        response = supabase.auth.sign_in_with_password(credentials)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

    return {'access_token': response.session.access_token}
