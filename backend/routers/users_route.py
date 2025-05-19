from fastapi import APIRouter, Depends, HTTPException
from prisma import Prisma
from pydantic import BaseModel, EmailStr

from ..prisma_client import get_prisma

router = APIRouter(prefix='/users', tags=['Users'])


class UserCreate(BaseModel):
    email: EmailStr
    name: str | None = None


class UserResponse(BaseModel):
    id: str
    email: str
    name: str | None
    createdAt: str
    updatedAt: str


@router.post('/', response_model=UserResponse)
async def create_user(
    user: UserCreate, prisma: Prisma = Depends(get_prisma)
) -> UserResponse:
    try:
        db_user = await prisma.user.create(
            data={
                'email': user.email,
                'name': user.name
            }
        )
        return UserResponse.model_validate(db_user)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Email already exists")


@router.get('/{user_id}', response_model=UserResponse)
async def get_user(
    user_id: str, prisma: Prisma = Depends(get_prisma)
) -> UserResponse:
    user = await prisma.user.find_unique(
        where={
            'id': user_id
        }
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(user)