from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..models.language import Language
from ..models.user_profile import (
    UserProfile,
    UserProfileCreate,
    UserProfileRead,
)

router = APIRouter(prefix="/user-profiles", tags=["User Profiles"])


@router.get("/", response_model=List[UserProfileRead])
def get_user_profiles(
    session: Annotated[Session, Depends(get_session)]
) -> List[UserProfileRead]:
    """
    Retrieve all user profiles.
    """
    statement = select(UserProfile)
    user_profiles = session.exec(statement).all()
    return user_profiles


@router.post("/", response_model=UserProfileRead)
def create_user_profile(
    user_profile: UserProfileCreate, session: Annotated[Session, Depends(get_session)]
) -> UserProfile:
    """
    Create a new user profile.
    """
    # Validate foreign key
    language = session.exec(
        select(Language).where(Language.code == user_profile.preferred_language)
    ).first()
    if not language:
        raise HTTPException(status_code=404, detail="Preferred language not found")

    db_user_profile = UserProfile(**user_profile.dict())
    session.add(db_user_profile)
    session.commit()
    session.refresh(db_user_profile)
    return db_user_profile


@router.put("/{user_id}", response_model=UserProfileRead)
def update_user_profile(
    user_id: UUID,
    updated_data: UserProfileCreate,
    session: Annotated[Session, Depends(get_session)],
) -> UserProfile:
    """
    Update an existing user profile.
    """
    user_profile = session.get(UserProfile, user_id)
    if not user_profile:
        raise HTTPException(status_code=404, detail="User profile not found")

    # Validate foreign key
    if updated_data.preferred_language:
        language = session.exec(
            select(Language).where(Language.code == updated_data.preferred_language)
        ).first()
        if not language:
            raise HTTPException(status_code=404, detail="Preferred language not found")

    for key, value in updated_data.dict().items():
        setattr(user_profile, key, value)

    session.add(user_profile)
    session.commit()
    session.refresh(user_profile)
    return user_profile


@router.delete("/{user_id}", response_model=dict)
def delete_user_profile(
    user_id: UUID, session: Annotated[Session, Depends(get_session)]
) -> dict:
    """
    Delete a user profile and cascade delete related entries.
    """
    user_profile = session.get(UserProfile, user_id)
    if not user_profile:
        raise HTTPException(status_code=404, detail="User profile not found")

    session.delete(user_profile)
    session.commit()
    return {"message": "User profile deleted successfully"}