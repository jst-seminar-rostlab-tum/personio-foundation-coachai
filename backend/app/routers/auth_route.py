from fastapi import APIRouter, HTTPException, status
from gotrue import AdminUserAttributes, SignUpWithPasswordCredentials
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


@router.post('/', response_model=str, status_code=status.HTTP_201_CREATED)
def create_user(req: CreateUserRequest) -> str:
    try:
        CreateUserRequest.model_validate(req)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        ) from e

    # TODO: Verify OTP code

    try:
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

    return 'User created successfully'
