from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import User, UserCreate, UserUpdate
from app.core.security import get_password_hash

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[User])
def read_users(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Get list of users"""
    from app.db.models import User as UserModel
    
    users = db.query(UserModel).offset(skip).limit(limit).all()
    return users


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserCreate, 
    db: Session = Depends(get_db)
):
    """Create new user"""
    from app.db.models import User as UserModel
    
    user = db.query(UserModel).filter(UserModel.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user = UserModel(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
