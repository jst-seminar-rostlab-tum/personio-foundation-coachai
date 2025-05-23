# Standard library imports

# Third-party imports
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr

from prisma import Prisma

# Local imports
from ..prisma_client import get_prisma

router = APIRouter(prefix='/users', tags=['Users'])

# Dependencies
get_prisma_dependency = Depends(get_prisma)


class UserCreate(BaseModel):
    email: EmailStr
    name: str | None = None


class UserResponse(BaseModel):
    id: str
    email: str
    name: str | None
    created_at: str
    updated_at: str


@router.post('/', response_model=UserResponse)
async def create_user(user: UserCreate, prisma: Prisma = get_prisma_dependency) -> UserResponse:
    try:
        db_user = await prisma.user.create(data={'email': user.email, 'name': user.name})
        return UserResponse.model_validate(db_user)
    except Exception as err:
        raise HTTPException(status_code=400, detail='Email already exists') from err


@router.get('/{user_id}', response_model=UserResponse)
async def get_user(user_id: str, prisma: Prisma = get_prisma_dependency) -> UserResponse:
    user = await prisma.user.find_unique(where={'id': user_id})
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    return UserResponse.model_validate(user)
