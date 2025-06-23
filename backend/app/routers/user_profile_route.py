from typing import Annotated, Optional, Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session as DBSession
from sqlmodel import select

from app.database import get_db_session
from app.dependencies import require_user
from app.models.conversation_scenario import ConversationScenario
from app.models.review import Review
from app.models.user_confidence_score import UserConfidenceScore
from app.models.user_goal import Goal, UserGoal
from app.models.user_profile import UserProfile
from app.schemas.user_confidence_score import ConfidenceScoreRead
from app.schemas.user_profile import (
    UserProfileExtendedRead,
    UserProfileRead,
    UserProfileReplace,
    UserProfileUpdate,
)

router = APIRouter(prefix='/user-profile', tags=['User Profiles'])


@router.get('', response_model=Union[list[UserProfileRead], list[UserProfileExtendedRead]])
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
                full_name=user.full_name,
                email=user.email,
                phone_number=user.phone_number,
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
                full_name=user.full_name,
                email=user.email,
                phone_number=user.phone_number,
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
    '/profile',
    response_model=Union[UserProfileRead, UserProfileExtendedRead],
)
def get_user_profile(
    user_profile: Annotated[UserProfile, Depends(require_user)],
    db_session: Annotated[DBSession, Depends(get_db_session)],
    detailed: bool = Query(False, description='Return extended profile details'),
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
            full_name=user.full_name,
            email=user.email,
            phone_number=user.phone_number,
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
            full_name=user.full_name,
            email=user.email,
            phone_number=user.phone_number,
            preferred_language_code=user.preferred_language_code,
            account_role=user.account_role,
            professional_role=user.professional_role,
            experience=user.experience,
            preferred_learning_style=user.preferred_learning_style,
            updated_at=user.updated_at,
            store_conversations=user.store_conversations,
        )


@router.put('', response_model=UserProfileExtendedRead)
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
    user.full_name = data.full_name
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
        full_name=user.full_name,
        email=user.email,
        phone_number=user.phone_number,
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


@router.patch('', response_model=UserProfileExtendedRead)
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
        full_name=user.full_name,
        email=user.email,
        phone_number=user.phone_number,
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


@router.delete('', response_model=dict)
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


@router.get('/export', response_model=dict)
def export_user_data(
    user_profile: Annotated[UserProfile, Depends(require_user)],
    db_session: Annotated[DBSession, Depends(get_db_session)],
) -> dict:
    """
    Export all user-related data (history) for the currently authenticated user.
    """
    user_id = user_profile.id

    # User profile
    user_data = {
        'profile': {
            'user_id': str(user_profile.id),
            'full_name': user_profile.full_name,
            'email': user_profile.email,
            'phone_number': user_profile.phone_number,
            'preferred_language_code': str(user_profile.preferred_language_code),
            'account_role': str(user_profile.account_role),
            'professional_role': str(user_profile.professional_role),
            'experience': str(user_profile.experience),
            'preferred_learning_style': str(user_profile.preferred_learning_style),
            'updated_at': user_profile.updated_at.isoformat() if user_profile.updated_at else None,
            'store_conversations': user_profile.store_conversations,
            'total_sessions': user_profile.total_sessions,
            'training_time': user_profile.training_time,
            'current_streak_days': user_profile.current_streak_days,
            'average_score': user_profile.average_score,
            'goals_achieved': user_profile.goals_achieved,
        },
        'goals': [],
        'confidence_scores': [],
        'scenarios': [],
        'scenario_preparations': [],
        'sessions': [],
        'session_turns': [],
        'session_feedback': [],
        'reviews': [],
    }

    # Goals
    goals = db_session.exec(select(UserGoal).where(UserGoal.user_id == user_id)).all()
    user_data['goals'] = [
        {
            'goal': str(goal.goal),
            'updated_at': goal.updated_at.isoformat() if goal.updated_at else None,
        }
        for goal in goals
    ]

    # Confidence Scores
    confidence_scores = db_session.exec(
        select(UserConfidenceScore).where(UserConfidenceScore.user_id == user_id)
    ).all()
    user_data['confidence_scores'] = [
        {
            'confidence_area': str(cs.confidence_area),
            'score': cs.score,
            'updated_at': cs.updated_at.isoformat() if cs.updated_at else None,
        }
        for cs in confidence_scores
    ]

    # Conversation Scenarios
    scenarios = db_session.exec(
        select(ConversationScenario).where(ConversationScenario.user_id == user_id)
    ).all()
    user_data['scenarios'] = [
        {
            'id': str(s.id),
            'category_id': s.category_id,
            'custom_category_label': s.custom_category_label,
            'language_code': str(s.language_code),
            'context': s.context,
            'goal': s.goal,
            'other_party': s.other_party,
            'difficulty_level': str(s.difficulty_level),
            'tone': s.tone,
            'complexity': s.complexity,
            'status': str(s.status),
            'created_at': s.created_at.isoformat() if s.created_at else None,
            'updated_at': s.updated_at.isoformat() if s.updated_at else None,
        }
        for s in scenarios
    ]

    # Scenario Preparations (for all scenarios)
    scenario_preparations = []
    for s in scenarios:
        if hasattr(s, 'preparation') and s.preparation:
            prep = s.preparation
            scenario_preparations.append(
                {
                    'id': str(prep.id),
                    'scenario_id': str(prep.scenario_id),
                    'objectives': prep.objectives,
                    'key_concepts': prep.key_concepts,
                    'prep_checklist': prep.prep_checklist,
                    'status': str(prep.status),
                    'created_at': prep.created_at.isoformat() if prep.created_at else None,
                    'updated_at': prep.updated_at.isoformat() if prep.updated_at else None,
                }
            )
    user_data['scenario_preparations'] = scenario_preparations

    # Sessions (linked to user's scenarios)
    sessions = []
    for scenario in scenarios:
        scenario_sessions = scenario.sessions
        for sess in scenario_sessions:
            sessions.append(sess)
    user_data['sessions'] = [
        {
            'id': str(sess.id),
            'scenario_id': str(sess.scenario_id),
            'scheduled_at': sess.scheduled_at.isoformat() if sess.scheduled_at else None,
            'started_at': sess.started_at.isoformat() if sess.started_at else None,
            'ended_at': sess.ended_at.isoformat() if sess.ended_at else None,
            'ai_persona': sess.ai_persona,
            'status': str(sess.status),
            'created_at': sess.created_at.isoformat() if sess.created_at else None,
            'updated_at': sess.updated_at.isoformat() if sess.updated_at else None,
        }
        for sess in sessions
    ]

    # Session Turns (for all sessions)
    session_turns = []
    for sess in sessions:
        for turn in sess.session_turns:
            session_turns.append(turn)
    user_data['session_turns'] = [
        {
            'id': str(turn.id),
            'session_id': str(turn.session_id),
            'speaker': str(turn.speaker),
            'start_offset_ms': turn.start_offset_ms,
            'end_offset_ms': turn.end_offset_ms,
            'text': turn.text,
            'audio_uri': turn.audio_uri,
            'ai_emotion': turn.ai_emotion,
            'created_at': turn.created_at.isoformat() if turn.created_at else None,
        }
        for turn in session_turns
    ]

    # Session Feedback (for all sessions)
    session_feedbacks = []
    for sess in sessions:
        if sess.feedback:
            session_feedbacks.append(sess.feedback)
    user_data['session_feedback'] = [
        {
            'id': str(fb.id),
            'session_id': str(fb.session_id),
            'scores': fb.scores,
            'tone_analysis': fb.tone_analysis,
            'overall_score': fb.overall_score,
            'transcript_uri': fb.transcript_uri,
            'speak_time_percent': fb.speak_time_percent,
            'questions_asked': fb.questions_asked,
            'session_length_s': fb.session_length_s,
            'goals_achieved': fb.goals_achieved,
            'example_positive': fb.example_positive,
            'example_negative': fb.example_negative,
            'recommendations': fb.recommendations,
            'status': str(fb.status),
            'created_at': fb.created_at.isoformat() if fb.created_at else None,
            'updated_at': fb.updated_at.isoformat() if fb.updated_at else None,
        }
        for fb in session_feedbacks
    ]

    # Reviews (by user)
    reviews = db_session.exec(select(Review).where(Review.user_id == user_id)).all()
    user_data['reviews'] = [
        {
            'id': str(r.id),
            'user_id': str(r.user_id),
            'session_id': str(r.session_id) if r.session_id else None,
            'rating': r.rating,
            'comment': r.comment,
            'created_at': r.created_at.isoformat() if r.created_at else None,
        }
        for r in reviews
    ]

    return user_data
