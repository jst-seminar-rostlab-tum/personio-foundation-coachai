from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..models.experience import Experience
from ..models.language import Language
from ..models.role import Role
from ..models.user_profile import (
    UserProfile,
    UserProfileCreate,
    UserProfileRead,
    UserProfileSignIn,
    UserProfileSignInResponse,
    UserProfileValidationResponse,
)

router = APIRouter(prefix='/user-profiles', tags=['User Profiles'])


@router.get('/', response_model=list[UserProfileRead])
def get_user_profiles(session: Annotated[Session, Depends(get_session)]) -> list[UserProfileRead]:
    """
    Retrieve all user profiles.
    """
    statement = select(UserProfile)
    user_profiles = session.exec(statement).all()
    return [UserProfileRead.model_validate(user_profile) for user_profile in user_profiles]


@router.post('/', response_model=UserProfileRead)
def create_user_profile(
    user_profile: UserProfileCreate, session: Annotated[Session, Depends(get_session)]
) -> UserProfile:
    """
    Create a new user profile.
    """
    # Set default language to English if not specified
    if not user_profile.preferred_language:
        user_profile.preferred_language = 'en'

    # Check if language exists
    language = session.exec(
        select(Language).where(Language.code == user_profile.preferred_language)
    ).first()

    if not language:
        raise HTTPException(status_code=404, detail='Preferred language not found')

    # Create new user profile
    db_user_profile = UserProfile(**user_profile.dict())
    session.add(db_user_profile)
    session.commit()
    session.refresh(db_user_profile)
    return db_user_profile


@router.put('/{user_id}', response_model=UserProfileRead)
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
        raise HTTPException(status_code=404, detail='User profile not found')

    # Check if email is being changed and if it already exists
    if updated_data.email != user_profile.email:
        existing_user = session.exec(
            select(UserProfile).where(UserProfile.email == updated_data.email)
        ).first()
        if existing_user:
            raise HTTPException(status_code=400, detail='Email already registered')

    # Validate language if it's being changed
    if updated_data.preferred_language:
        language = session.exec(
            select(Language).where(Language.code == updated_data.preferred_language)
        ).first()
        if not language:
            raise HTTPException(status_code=404, detail='Preferred language not found')

    for key, value in updated_data.dict().items():
        setattr(user_profile, key, value)

    session.add(user_profile)
    session.commit()
    session.refresh(user_profile)
    return user_profile


@router.delete('/{user_id}', response_model=dict)
def delete_user_profile(user_id: UUID, session: Annotated[Session, Depends(get_session)]) -> dict:
    """
    Delete a user profile and cascade delete related entries.
    """
    user_profile = session.get(UserProfile, user_id)
    if not user_profile:
        raise HTTPException(status_code=404, detail='User profile not found')

    session.delete(user_profile)
    session.commit()
    return {'message': 'User profile deleted successfully'}


@router.post('/sign-in', response_model=UserProfileSignInResponse)
def sign_in(
    credentials: UserProfileSignIn, session: Annotated[Session, Depends(get_session)]
) -> UserProfileSignInResponse:
    """
    Sign in a user with email and password.
    """
    # Find user by email
    user = session.exec(select(UserProfile).where(UserProfile.email == credentials.email)).first()

    if not user:
        raise HTTPException(status_code=401, detail='Invalid email or password')

    # Verify password
    if user.password != credentials.password:  # In production, use proper password hashing
        raise HTTPException(status_code=401, detail='Invalid email or password')

    # Convert UserProfile to UserProfileSignInResponse
    return UserProfileSignInResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        preferred_language=user.preferred_language,
        role_id=user.role_id,
        experience_id=user.experience_id,
        preferred_learning_style=user.preferred_learning_style,
        preferred_session_length=user.preferred_session_length,
    )


@router.post('/validate', response_model=UserProfileValidationResponse)
def validate_user_profile(
    user_profile: UserProfileCreate, session: Annotated[Session, Depends(get_session)]
) -> UserProfileValidationResponse:
    """
    Validate user profile data before creation.
    Checks for existing email, phone number, and full name.
    """
    errors = {}

    # Check if email already exists
    existing_email = session.exec(
        select(UserProfile).where(UserProfile.email == user_profile.email)
    ).first()
    if existing_email:
        errors['email'] = 'Email already registered'

    # Check if phone number already exists
    existing_phone = session.exec(
        select(UserProfile).where(UserProfile.phone_number == user_profile.phone_number)
    ).first()
    if existing_phone:
        errors['phone_number'] = 'Phone number already registered'

    # Check if full name already exists
    existing_name = session.exec(
        select(UserProfile).where(UserProfile.full_name == user_profile.full_name)
    ).first()
    if existing_name:
        errors['full_name'] = 'Full name already registered'

    # Check if language exists
    language = session.exec(
        select(Language).where(Language.code == user_profile.preferred_language)
    ).first()
    if not language:
        errors['preferred_language'] = 'Preferred language not found'

    # Only validate UUIDs if they are provided
    if user_profile.role_id:
        role = session.get(Role, user_profile.role_id)
        if not role:
            errors['role_id'] = 'Invalid role selected'

    if user_profile.experience_id:
        experience = session.get(Experience, user_profile.experience_id)
        if not experience:
            errors['experience_id'] = 'Invalid experience level selected'

    if errors:
        return UserProfileValidationResponse(
            message='Validation failed', is_valid=False, errors=errors
        )

    return UserProfileValidationResponse(message='Validation successful', is_valid=True)
