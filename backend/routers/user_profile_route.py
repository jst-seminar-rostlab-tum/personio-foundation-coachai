from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..models.language import Language
from ..models.user_confidence_score import ConfidenceScoreRead, UserConfidenceScore
from ..models.user_goal import UserGoal
from ..models.user_profile import (
    UserProfile,
    UserProfileCreate,
    UserProfileExtendedRead,
    UserProfileRead,
    UserProfileSignIn,
    UserProfileSignInResponse,
    UserProfileValidate,
    UserProfileValidationResponse,
)

router = APIRouter(prefix='/user-profiles', tags=['User Profiles'])


@router.get('/user_ids', response_model=list[UserProfileRead])
def get_user_profile_ids(
    session: Annotated[Session, Depends(get_session)],
) -> list[UserProfileRead]:
    """
    Retrieve all user profiles with their associated goals and confidence scores. (IDS)
    Returns a list of user profiles in a simplified format.
    """
    statement = select(UserProfile)
    users = session.exec(statement).all()

    user_profiles = []
    for user in users:
        # Retrieve goal IDs for the user
        goal_statement = select(UserGoal.goal_id).where(UserGoal.user_id == user.id)
        goals = session.exec(goal_statement).all()

        # Retrieve confidence score IDs for the user
        confidence_statement = select(UserConfidenceScore.area_id).where(
            UserConfidenceScore.user_id == user.id
        )
        confidence_scores = session.exec(confidence_statement).all()

        # Serialize the UserProfile object into UserProfileRead schema
        user_profiles.append(
            UserProfileRead(
                id=user.id,
                preferred_language=user.preferred_language,
                role_id=user.role_id,
                experience_id=user.experience_id,
                preferred_learning_style_id=user.preferred_learning_style_id,
                preferred_session_length_id=user.preferred_session_length_id,
                goal=list(goals),
                confidence_scores=list(confidence_scores),
                updated_at=user.updated_at,
                store_conversations=user.store_conversations,
            )
        )

    return user_profiles


@router.get('/{user_id}', response_model=UserProfileExtendedRead)
def get_user_profile_by_id(
    user_id: str, session: Annotated[Session, Depends(get_session)]
) -> UserProfileExtendedRead:
    """
    Retrieve a single user profile by its unique user ID.
    Includes detailed information such as goals and confidence scores. (VALUES)
    """
    statement = select(UserProfile).where(UserProfile.id == user_id)
    user = session.exec(statement).first()

    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    confidence_scores = [
        ConfidenceScoreRead(area_label=score.confidence_area.label, score=score.score)
        for score in user.user_confidence_scores
        if score.confidence_area and score.confidence_area.label
    ]

    user_data = UserProfileExtendedRead(
        user_id=user.id,
        preferred_language=user.preferred_language,
        role=user.role.label if user.role else None,
        experience=user.experience.label if user.experience else None,
        preferred_learning_style=user.preferred_learning_style.label
        if user.preferred_learning_style
        else None,
        preferred_session_length=user.preferred_session_length.label
        if user.preferred_session_length
        else None,
        goal=[
            user_goal.goal.label
            for user_goal in user.user_goals
            if user_goal.goal and user_goal.goal.label
        ],
        confidence_scores=confidence_scores,
        store_conversations=user.store_conversations,
    )

    return user_data


@router.get('/', response_model=list[UserProfileExtendedRead])
def get_user_profiles(
    session: Annotated[Session, Depends(get_session)],
) -> list[UserProfileExtendedRead]:
    """
    Retrieve all user profiles with detailed information.
    Includes goals and confidence scores for each user profile. (VALUES)
    """
    statement = select(UserProfile)
    results = session.exec(statement).all()

    user_map = {}

    for user in results:
        uid = str(user.id)

        if uid not in user_map:
            user_map[uid] = {
                'user_id': uid,
                'preferred_language': user.preferred_language,
                'role': user.role.label if user.role else None,
                'experience': user.experience.label if user.experience else None,
                'preferred_learning_style': user.preferred_learning_style.label
                if user.preferred_learning_style
                else None,
                'preferred_session_length': user.preferred_session_length.label
                if user.preferred_session_length
                else None,
                'goal': set(),
                'confidence_scores': set(),
            }

        # Add goal if present
        if user.user_goals:
            for user_goal in user.user_goals:
                if user_goal.goal and user_goal.goal.label:
                    user_map[uid]['goal'].add(user_goal.goal.label)

        # Add confidence score if present
        if user.user_confidence_scores:
            for score in user.user_confidence_scores:
                if score.confidence_area and score.confidence_area.label:
                    user_map[uid]['confidence_scores'].add(
                        (score.confidence_area.label, score.score)
                    )

    # Convert sets to lists of dicts
    final_result = []
    for user_data in user_map.values():
        confidence_scores = [
            ConfidenceScoreRead(area_label=label, score=score)
            for label, score in user_data['confidence_scores']
        ]

        final_result.append(
            UserProfileExtendedRead(
                user_id=user_data['user_id'],
                preferred_language=user_data['preferred_language'],
                role=user_data['role'],
                experience=user_data['experience'],
                preferred_learning_style=user_data['preferred_learning_style'],
                preferred_session_length=user_data['preferred_session_length'],
                goal=list(user_data['goal']),
                confidence_scores=confidence_scores,
                store_conversations=user_data['store_conversations'],
            )
        )

    return final_result


@router.post('/', response_model=UserProfile)
def create_user_profile(
    user_profile: UserProfileCreate,
    session: Annotated[Session, Depends(get_session)],
) -> UserProfile:
    """
    Create a new user profile with associated goals and confidence scores.
    Accepts user data as input.
    """

    # Check if language exists, if not create it
    language = session.exec(
        select(Language).where(Language.code == user_profile.preferred_language)
    ).first()

    print(language)

    if not language:
        # Create English language if it doesn't exist
        language = Language(code='en', name='English')
        session.add(language)
        session.commit()
        session.refresh(language)

    print(language)
    # Set default language to English if not specified
    if not user_profile.preferred_language:
        user_profile.preferred_language = 'en'

    print(user_profile)
    # Create new user profile with only required fields
    db_user_profile = UserProfile(
        preferred_language=user_profile.preferred_language,
        role_id=user_profile.role_id,
        experience_id=user_profile.experience_id,
        preferred_learning_style_id=user_profile.preferred_learning_style_id,
        preferred_session_length_id=user_profile.preferred_session_length_id,
        full_name=user_profile.full_name,
        email=user_profile.email,
        phone_number=user_profile.phone_number,
        password=user_profile.password,
    )
    session.add(db_user_profile)
    session.commit()
    session.refresh(db_user_profile)

    return db_user_profile


@router.put('/{user_id}', response_model=UserProfile)
def update_user_profile(
    user_id: UUID,
    user_data: UserProfileCreate,  # Expect full data for PUT
    session: Annotated[Session, Depends(get_session)],
) -> UserProfile:
    """
    Fully update an existing user profile with new data.
    Requires all fields to be provided.
    """
    user = session.get(UserProfile, user_id)

    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    # Update UserProfile fields
    user.role_id = user_data.role_id
    user.experience_id = user_data.experience_id
    user.preferred_language = user_data.preferred_language
    user.preferred_learning_style_id = user_data.preferred_learning_style_id
    user.preferred_session_length_id = user_data.preferred_session_length_id
    user.store_conversations = user_data.store_conversations

    session.add(user)

    # Update goals
    statement = select(UserGoal).where(UserGoal.user_id == user_id)
    user_goals = session.exec(statement)
    for user_goal in user_goals:
        session.delete(user_goal)
    session.commit()  # Commit to remove old goals
    for goal_id in user_data.goal_ids:
        user_goal = UserGoal(user_id=user.id, goal_id=goal_id)
        session.add(user_goal)

    # Update confidence scores
    statement = select(UserConfidenceScore).where(UserConfidenceScore.user_id == user_id)
    user_confidence_scores = session.exec(statement)
    for user_confidence_score in user_confidence_scores:
        session.delete(user_confidence_score)
    session.commit()
    for confidence_score in user_data.confidence_scores:
        user_confidence_score = UserConfidenceScore(
            user_id=user.id,
            area_id=confidence_score['area_id'],
            score=confidence_score['score'],
        )
        session.add(user_confidence_score)

    session.commit()
    session.refresh(user)

    return user


@router.patch('/{user_id}', response_model=UserProfile)
def patch_user_profile(
    user_id: UUID,
    user_data: dict,  # Expect partial data for PATCH
    session: Annotated[Session, Depends(get_session)],
) -> UserProfile:
    """
    Update an existing user profile.
    """
    user = session.get(UserProfile, user_id)
    if not user:
        raise HTTPException(status_code=404, detail='User profile not found')

    # Update UserProfile fields if provided
    if 'role_id' in user_data:
        user.role_id = user_data['role_id']
    if 'experience_id' in user_data:
        user.experience_id = user_data['experience_id']
    if 'preferred_language' in user_data:
        user.preferred_language = user_data['preferred_language']
    if 'preferred_learning_style_id' in user_data:
        user.preferred_learning_style_id = user_data['preferred_learning_style_id']
    if 'preferred_session_length_id' in user_data:
        user.preferred_session_length_id = user_data['preferred_session_length_id']
    if 'store_conversations' in user_data:
        user.store_conversations = user_data['store_conversations']

    session.add(user)

    # Update goals if provided
    if 'goal_ids' in user_data:
        statement = select(UserGoal).where(UserGoal.user_id == user_id)
        user_goals = session.exec(statement)
        for user_goal in user_goals:
            session.delete(user_goal)
        session.commit()  # Commit to remove old goals
        for goal_id in user_data['goal_ids']:
            user_goal = UserGoal(user_id=user.id, goal_id=goal_id)
            session.add(user_goal)

    # Update confidence scores if provided
    if 'confidence_scores' in user_data:
        statement = select(UserConfidenceScore).where(UserConfidenceScore.user_id == user_id)
        user_confidence_scores = session.exec(statement)
        for user_confidence_score in user_confidence_scores:
            session.delete(user_confidence_score)
        session.commit()
        for confidence_score in user_data['confidence_scores']:
            user_confidence_score = UserConfidenceScore(
                user_id=user.id,
                area_id=confidence_score['area_id'],
                score=confidence_score['score'],
            )
            session.add(user_confidence_score)

    session.commit()
    session.refresh(user)

    return user


@router.delete('/{user_id}', response_model=dict)
def delete_user_profile(user_id: UUID, session: Annotated[Session, Depends(get_session)]) -> dict:
    """
    Delete a user profile by its unique user ID.
    Cascades the deletion to related goals and confidence scores.
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
    user_profile: UserProfileValidate, session: Annotated[Session, Depends(get_session)]
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

    if errors:
        return UserProfileValidationResponse(
            message='Validation failed', is_valid=False, errors=errors
        )

    return UserProfileValidationResponse(message='Validation successful', is_valid=True)
