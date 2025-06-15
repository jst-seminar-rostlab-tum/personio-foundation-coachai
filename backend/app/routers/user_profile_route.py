from typing import Annotated, Optional, Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session as DBSession
from sqlmodel import select

from app.database import get_db_session
from app.dependencies import require_user
from app.models.user_confidence_score import ConfidenceScoreRead, UserConfidenceScore
from app.models.user_goal import Goal, UserGoal
from app.models.user_profile import (
    UserProfile,
    UserProfileCreate,
    UserProfileExtendedRead,
    UserProfileRead,
    UserProfileReplace,
    UserProfileUpdate,
)

router = APIRouter(prefix='/user-profile', tags=['User Profiles'])


@router.get('/', response_model=Union[list[UserProfileRead], list[UserProfileExtendedRead]])
def get_user_profiles(
    db_session: Annotated[DBSession, Depends(get_db_session)],
    detailed: bool = False,
) -> Union[list[UserProfileRead], list[UserProfileExtendedRead]]:
    """
    Retrieve all user profiles.

    - If `detailed` is False (default), returns simplified profiles.

    - If `detailed` is True, returns extended profiles including goals and confidence scores.
    """
    statement = select(UserProfile)
    users = db_session.exec(statement).all()

    if detailed:
        return [
            UserProfileExtendedRead(
                user_id=user.id,
                preferred_language_code=user.preferred_language_code,
                account_role=user.account_role,
                professional_role=user.professional_role,
                experience=user.experience,
                preferred_learning_style=user.preferred_learning_style,
                goals=[goal.goal for goal in user.user_goals],
                confidence_scores=[
                    ConfidenceScoreRead(
                        confidence_area=cs.confidence_area,
                        score=cs.score,
                    )
                    for cs in user.user_confidence_scores
                ],
                updated_at=user.updated_at,
                store_conversations=user.store_conversations,
            )
            for user in users
        ]
    else:
        return [
            UserProfileRead(
                user_id=user.id,
                preferred_language_code=user.preferred_language_code,
                account_role=user.account_role,
                professional_role=user.professional_role,
                experience=user.experience,
                preferred_learning_style=user.preferred_learning_style,
                updated_at=user.updated_at,
                store_conversations=user.store_conversations,
            )
            for user in users
        ]


@router.get(
    '/profile/',
    response_model=Union[UserProfileRead, UserProfileExtendedRead],
)
def get_user_profile(
    user_profile: Annotated[UserProfile, Depends(require_user)],
    db_session: Annotated[DBSession, Depends(get_db_session)],
    detailed: bool = False,
) -> Union[UserProfileRead, UserProfileExtendedRead]:
    """
    Retrieve a single user profile.

    - If `detailed` is False (default), returns simplified profiles.

    - If `detailed` is True, returns extended profiles including goals and confidence scores.
    """
    user_id = user_profile.id
    statement = select(UserProfile).where(UserProfile.id == user_id)
    user = db_session.exec(statement).first()

    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    if detailed:
        return UserProfileExtendedRead(
            user_id=user.id,
            preferred_language_code=user.preferred_language_code,
            account_role=user.account_role,
            professional_role=user.professional_role,
            experience=user.experience,
            preferred_learning_style=user.preferred_learning_style,
            goals=[goal.goal for goal in user.user_goals],
            confidence_scores=[
                ConfidenceScoreRead(
                    confidence_area=cs.confidence_area,
                    score=cs.score,
                )
                for cs in user.user_confidence_scores
            ],
            updated_at=user.updated_at,
            store_conversations=user.store_conversations,
        )
    else:
        return UserProfileRead(
            user_id=user.id,
            preferred_language_code=user.preferred_language_code,
            account_role=user.account_role,
            professional_role=user.professional_role,
            experience=user.experience,
            preferred_learning_style=user.preferred_learning_style,
            updated_at=user.updated_at,
            store_conversations=user.store_conversations,
        )


@router.post(
    '/',
    response_model=UserProfileExtendedRead,
    status_code=201,
    dependencies=[Depends(require_user)],
)
def create_user_profile(
    data: UserProfileCreate,
    db_session: Annotated[DBSession, Depends(get_db_session)],
) -> UserProfileExtendedRead:
    # Check if user already exists
    existing_user = db_session.get(UserProfile, data.user_id)
    if existing_user:
        raise HTTPException(status_code=409, detail='User already exists')

    # Create new user profile
    user = UserProfile(
        id=data.user_id,
        account_role=data.account_role,
        experience=data.experience,
        preferred_language_code=data.preferred_language_code,
        preferred_learning_style=data.preferred_learning_style,
        store_conversations=data.store_conversations,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Create goals
    for goal in data.goals:
        user_goal = UserGoal(user_id=user.id, goal=Goal(goal))
        db_session.add(user_goal)

    # Create confidence scores
    for confidence_score in data.confidence_scores:
        user_confidence_score = UserConfidenceScore(
            user_id=user.id,
            confidence_area=confidence_score.confidence_area,
            score=confidence_score.score,
        )
        db_session.add(user_confidence_score)

    db_session.commit()
    db_session.refresh(user)

    return UserProfileExtendedRead(
        user_id=user.id,
        preferred_language_code=user.preferred_language_code,
        account_role=user.account_role,
        professional_role=user.professional_role,
        experience=user.experience,
        preferred_learning_style=user.preferred_learning_style,
        goals=[g.goal for g in user.user_goals],
        confidence_scores=[
            ConfidenceScoreRead(
                confidence_area=cs.confidence_area,
                score=cs.score,
            )
            for cs in user.user_confidence_scores
        ],
        updated_at=user.updated_at,
        store_conversations=user.store_conversations,
    )


@router.put('/', response_model=UserProfileExtendedRead)
def replace_user_profile(
    user_profile: Annotated[UserProfile, Depends(require_user)],
    data: UserProfileReplace,
    db_session: Annotated[DBSession, Depends(get_db_session)],
) -> UserProfileExtendedRead:
    user_id = user_profile.id
    user = db_session.get(UserProfile, user_id)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    # Update UserProfile fields
    user.account_role = data.account_role
    user.experience = data.experience
    user.preferred_language_code = data.preferred_language_code
    user.preferred_learning_style = data.preferred_learning_style
    user.store_conversations = data.store_conversations
    user.professional_role = data.professional_role

    db_session.add(user)

    # Update goals
    statement = select(UserGoal).where(UserGoal.user_id == user_id)
    user_goals = db_session.exec(statement)
    for user_goal in user_goals:
        db_session.delete(user_goal)
    db_session.commit()  # Commit to remove old goals

    for goal in data.goals:
        user_goal = UserGoal(user_id=user.id, goal=Goal(goal))
        db_session.add(user_goal)

    # Update confidence scores
    statement = select(UserConfidenceScore).where(UserConfidenceScore.user_id == user_id)
    user_confidence_scores = db_session.exec(statement)
    for user_confidence_score in user_confidence_scores:
        db_session.delete(user_confidence_score)
    db_session.commit()

    for confidence_score in data.confidence_scores:
        user_confidence_score = UserConfidenceScore(
            user_id=user.id,
            confidence_area=confidence_score.confidence_area,
            score=confidence_score.score,
        )
        db_session.add(user_confidence_score)

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return UserProfileExtendedRead(
        user_id=user.id,
        preferred_language_code=user.preferred_language_code,
        account_role=user.account_role,
        professional_role=user.professional_role,
        experience=user.experience,
        preferred_learning_style=user.preferred_learning_style,
        goals=[g.goal for g in user.user_goals],
        confidence_scores=[
            ConfidenceScoreRead(
                confidence_area=cs.confidence_area,
                score=cs.score,
            )
            for cs in user.user_confidence_scores
        ],
        updated_at=user.updated_at,
        store_conversations=user.store_conversations,
    )


@router.patch('/', response_model=UserProfileExtendedRead)
def update_user_profile(
    user_profile: Annotated[UserProfile, Depends(require_user)],
    data: UserProfileUpdate,
    db_session: Annotated[DBSession, Depends(get_db_session)],
) -> UserProfileExtendedRead:
    user_id = user_profile.id
    user = db_session.get(UserProfile, user_id)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    update_data = data.dict(exclude_unset=True)

    # Update simple fields if provided
    if 'account_role' in update_data:
        user.account_role = update_data['account_role']
    if 'experience' in update_data:
        user.experience = update_data['experience']
    if 'preferred_language_code' in update_data:
        user.preferred_language_code = update_data['preferred_language_code']
    if 'preferred_learning_style' in update_data:
        user.preferred_learning_style = update_data['preferred_learning_style']
    if 'store_conversations' in update_data:
        user.store_conversations = update_data['store_conversations']
    if 'professional_role' in update_data:
        user.professional_role = update_data['professional_role']

    db_session.add(user)

    # Update goals if provided
    if 'goals' in update_data:
        statement = select(UserGoal).where(UserGoal.user_id == user_id)
        user_goals = db_session.exec(statement)
        for user_goal in user_goals:
            db_session.delete(user_goal)
        db_session.commit()

        for goal in update_data['goals']:
            db_session.add(UserGoal(user_id=user.id, goal=Goal(goal)))

    # Update confidence scores if provided
    if 'confidence_scores' in update_data:
        statement = select(UserConfidenceScore).where(UserConfidenceScore.user_id == user_id)
        user_confidence_scores = db_session.exec(statement)
        for cs in user_confidence_scores:
            db_session.delete(cs)
        db_session.commit()

        for cs_data in data.confidence_scores:
            db_session.add(
                UserConfidenceScore(
                    user_id=user.id,
                    confidence_area=cs_data.confidence_area,
                    score=cs_data.score,
                )
            )

    db_session.commit()
    db_session.refresh(user)

    return UserProfileExtendedRead(
        user_id=user.id,
        preferred_language_code=user.preferred_language_code,
        account_role=user.account_role,
        professional_role=user.professional_role,
        experience=user.experience,
        preferred_learning_style=user.preferred_learning_style,
        goals=[g.goal for g in user.user_goals],
        confidence_scores=[
            ConfidenceScoreRead(
                confidence_area=cs.confidence_area,
                score=cs.score,
            )
            for cs in user.user_confidence_scores
        ],
        updated_at=user.updated_at,
        store_conversations=user.store_conversations,
    )


@router.delete('/', response_model=dict)
def delete_user_profile(
    user_profile: Annotated[UserProfile, Depends(require_user)],
    db_session: Annotated[DBSession, Depends(get_db_session)],
    delete_user_id: Optional[UUID] = None,
) -> dict:
    """
    Delete a user profile by its unique user ID.
    Cascades the deletion to related goals and confidence scores.
    """
    user_id = user_profile.id
    if delete_user_id and user_profile.account_role == 'admin':
        user_id = delete_user_id
    elif delete_user_id and delete_user_id != user_profile.id:
        raise HTTPException(status_code=403, detail='Admin access required to delete other users')

    user_profile = db_session.get(UserProfile, user_id)  # type: ignore
    if not user_profile:
        raise HTTPException(status_code=404, detail='User profile not found')
    db_session.delete(user_profile)
    db_session.commit()
    return {'message': 'User profile deleted successfully'}
