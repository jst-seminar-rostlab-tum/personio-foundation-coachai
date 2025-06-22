import logging
from datetime import UTC, datetime
from math import ceil
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlmodel import Session as DBSession
from sqlmodel import col, select

from app.database import get_db_session
from app.dependencies import require_user
from app.models.admin_dashboard_stats import AdminDashboardStats
from app.models.conversation_category import ConversationCategory
from app.models.conversation_scenario import ConversationScenario
from app.models.scenario_preparation import ScenarioPreparation, ScenarioPreparationStatus
from app.models.session import Session, SessionStatus
from app.models.session_feedback import FeedbackStatusEnum, SessionFeedback
from app.models.session_turn import SessionTurn
from app.models.user_profile import AccountRole, UserProfile
from app.schemas.session import (
    SessionCreate,
    SessionDetailsRead,
    SessionRead,
    SessionUpdate,
)
from app.schemas.session_feedback import ExamplesRequest, SessionFeedbackMetrics
from app.schemas.sessions_paginated import (
    PaginatedSessionsResponse,
    SessionItem,
    SkillScores,
)
from app.services.session_feedback_service import generate_and_store_feedback

router = APIRouter(prefix='/session', tags=['Sessions'])


# Endpoint to get session details by ID
@router.get('/{session_id}', response_model=SessionDetailsRead)
def get_session_by_id(
    session_id: UUID,
    db_session: Annotated[DBSession, Depends(get_db_session)],
    user_profile: Annotated[UserProfile, Depends(require_user)],
) -> SessionDetailsRead:
    """
    Retrieve a session by its ID.
    """
    session = db_session.get(Session, session_id)
    if not session:
        raise HTTPException(status_code=404, detail='No session found with the given ID')

    # Get session title from the conversation scenario
    conversation_scenario = db_session.get(ConversationScenario, session.scenario_id)
    if not conversation_scenario:
        raise HTTPException(
            status_code=404, detail='No conversation scenario found for the session'
        )

    # Test if the session is the session of the user or the user is an admin
    user_id = user_profile.id
    if conversation_scenario.user_id != user_id and user_profile.account_role != AccountRole.admin:
        raise HTTPException(
            status_code=403, detail='You do not have permission to access this session'
        )

    if conversation_scenario.category:
        training_title = conversation_scenario.category.name
    elif conversation_scenario.custom_category_label:
        training_title = conversation_scenario.custom_category_label
    else:
        training_title = 'No Title available'

    if conversation_scenario.preparation:
        goals = conversation_scenario.preparation.objectives
    else:
        goals = []

    session_response = SessionDetailsRead(
        id=session.id,
        scenario_id=session.scenario_id,
        scheduled_at=session.scheduled_at,
        started_at=session.started_at,
        ended_at=session.ended_at,
        ai_persona=session.ai_persona,
        status=session.status,
        created_at=session.created_at,
        updated_at=session.updated_at,
        title=training_title,
        summary=(
            'The person giving feedback was rude but the person receiving feedback took it well.'
        ),  # mocked
        goals_total=goals,
    )

    # Fetch the associated conversation turns and their audio URIs
    session_turns = db_session.exec(
        select(SessionTurn).where(SessionTurn.session_id == session_id)
    ).all()

    if session_turns:
        session_response.audio_uris = [turn.audio_uri for turn in session_turns]

    # Fetch the asociated Feedback for the session
    feedback = db_session.exec(
        select(SessionFeedback).where(SessionFeedback.session_id == session_id)
    ).first()

    if not feedback or feedback.status == FeedbackStatusEnum.pending:
        raise HTTPException(status_code=202, detail='Session feedback in progress.')
    elif feedback and feedback.status == FeedbackStatusEnum.failed:
        raise HTTPException(status_code=500, detail='Session feedback failed.')
    else:
        session_response.feedback = SessionFeedbackMetrics(
            scores=feedback.scores,
            tone_analysis=feedback.tone_analysis,
            overall_score=feedback.overall_score,
            transcript_uri=feedback.transcript_uri,
            speak_time_percent=feedback.speak_time_percent,
            questions_asked=feedback.questions_asked,
            session_length_s=feedback.session_length_s,
            goals_achieved=feedback.goals_achieved,
            example_positive=feedback.example_positive,  # type: ignore
            example_negative=feedback.example_negative,  # type: ignore
            recommendations=feedback.recommendations,  # type: ignore
        )

    return session_response


# Endpoint to get paginated list of sessions for a user
@router.get('', response_model=PaginatedSessionsResponse)
def get_sessions(
    user_profile: Annotated[UserProfile, Depends(require_user)],
    db_session: Annotated[DBSession, Depends(get_db_session)],
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
) -> PaginatedSessionsResponse:
    """
    Return paginated list of completed sessions for a user.
    """
    user_id = user_profile.id

    statement = select(ConversationScenario.id).where(ConversationScenario.user_id == user_id)
    scenario_ids = db_session.exec(statement).all()

    if not scenario_ids:
        return PaginatedSessionsResponse(
            page=page,
            limit=page_size,
            total_pages=0,
            total_sessions=0,
            sessions=[],
        )

    # Query sessions
    session_query = (
        select(Session)
        .where(col(Session.scenario_id).in_(scenario_ids))
        .order_by(col(Session.created_at).desc())
    )

    total_sessions = len(db_session.exec(session_query).all())
    sessions = db_session.exec(session_query.offset((page - 1) * page_size).limit(page_size)).all()

    session_list = []
    for sess in sessions:
        conversation_scenario = db_session.exec(
            select(ConversationScenario).where(ConversationScenario.id == sess.scenario_id)
        ).first()
        if not conversation_scenario:
            raise HTTPException(status_code=404, detail='Conversation scenario not found')

        conversation_category = None
        if conversation_scenario.category_id:
            conversation_category = db_session.exec(
                select(ConversationCategory).where(
                    ConversationCategory.id == conversation_scenario.category_id
                )
            ).first()
            if not conversation_category:
                raise HTTPException(status_code=404, detail='Conversation Category not found')

        item = SessionItem(
            session_id=sess.id,
            title=conversation_category.name if conversation_category else 'No Title',
            summary=conversation_category.name
            if conversation_category
            else 'No Summary',  # TODO: add summary to conversation_category
            status=sess.status,
            date=sess.ended_at,
            score=82,  # mocked
            skills=SkillScores(
                structure=85,
                empathy=70,
                solution_focus=75,
                clarity=70,
            ),  # mocked
        )
        session_list.append(item)

    return PaginatedSessionsResponse(
        page=page,
        limit=page_size,
        total_pages=ceil(total_sessions / page_size),
        total_sessions=total_sessions,
        sessions=session_list,
    )


# Endpoint to create a new session
@router.post('', response_model=SessionRead, dependencies=[Depends(require_user)])
def create_session(
    session_data: SessionCreate, db_session: Annotated[DBSession, Depends(get_db_session)]
) -> Session:
    """
    Create a new session.
    """
    # Validate foreign keys
    conversation_scenario = db_session.get(ConversationScenario, session_data.scenario_id)
    if not conversation_scenario:
        raise HTTPException(status_code=404, detail='Conversation scenario not found')
    new_session = Session(**session_data.model_dump())
    new_session.status = SessionStatus.started
    new_session.started_at = datetime.now(UTC)

    db_session.add(new_session)
    db_session.commit()
    db_session.refresh(new_session)
    return new_session


# Endpoint to update an existing session
@router.put('/{session_id}', response_model=SessionRead)
def update_session(
    session_id: UUID,
    updated_data: SessionUpdate,
    db_session: Annotated[DBSession, Depends(get_db_session)],
    background_tasks: BackgroundTasks,
    user_profile: Annotated[UserProfile, Depends(require_user)],
) -> Session:
    """
    Update an existing session.
    """
    session = db_session.get(Session, session_id)
    if not session:
        raise HTTPException(status_code=404, detail='Session not found')

    # Forbid updates to completed sessions for non-admin users
    if session.status == SessionStatus.completed and user_profile.account_role != AccountRole.admin:
        raise HTTPException(status_code=400, detail='A completed session cannot be updated.')

    previous_status = session.status

    scenario_id = updated_data.scenario_id or session.scenario_id
    conversation_scenario = db_session.get(ConversationScenario, scenario_id)
    if not conversation_scenario:
        raise HTTPException(status_code=404, detail='Conversation scenario not found')

    for key, value in updated_data.model_dump(exclude_unset=True).items():
        setattr(session, key, value)

    # Check if the session status is changing to completed
    if (
        previous_status != SessionStatus.completed
        and updated_data.status == SessionStatus.completed
        and session.feedback is None
    ):
        session.ended_at = datetime.now(UTC)

        statement = select(ScenarioPreparation).where(
            ScenarioPreparation.scenario_id == session.scenario_id
        )
        preparation = db_session.exec(statement).first()
        if not preparation:
            raise HTTPException(
                status_code=400, detail='No preparation steps found for the given scenario'
            )
        if preparation.status != ScenarioPreparationStatus.completed:
            raise HTTPException(
                status_code=400,
                detail='Preparation steps must be completed before generating feedback',
            )

        session_turns = db_session.exec(
            select(SessionTurn).where(SessionTurn.session_id == session.id)
        ).all()

        transcripts = None
        if session_turns:
            transcripts = '\n'.join([f'{turn.speaker}: {turn.text}' for turn in session_turns])

        category = db_session.exec(
            select(ConversationCategory).where(
                ConversationCategory.id == conversation_scenario.category_id
            )
        ).first()
        if not category:
            raise HTTPException(
                status_code=404, detail='Conversation category not found for the session'
            )

        key_concepts = preparation.key_concepts
        key_concepts_str = '\n'.join(f'{item["header"]}: {item["value"]}' for item in key_concepts)

        request = ExamplesRequest(
            category=category.name,
            goal=conversation_scenario.goal,
            context=conversation_scenario.context,
            other_party=conversation_scenario.other_party,
            transcript=transcripts,
            objectives=preparation.objectives,
            key_concepts=key_concepts_str,
            language_code=conversation_scenario.language_code,
        )

        # Schedule the feedback generation in the background
        background_tasks.add_task(
            generate_and_store_feedback,
            session_id=session.id,
            example_request=request,
            db_session=db_session,
        )

        # === Update user statistics ===
        assert session.started_at is not None and session.ended_at is not None
        started_at = (
            session.started_at.replace(tzinfo=UTC)
            if session.started_at.tzinfo is None
            else session.started_at
        )
        ended_at = (
            session.ended_at.replace(tzinfo=UTC)
            if session.ended_at.tzinfo is None
            else session.ended_at
        )
        session_length = (ended_at - started_at).total_seconds() / 3600  # in hours
        user_profile.total_sessions = (user_profile.total_sessions or 0) + 1
        user_profile.training_time = (user_profile.training_time or 0) + session_length
        user_profile.updated_at = datetime.now(UTC)
        db_session.add(user_profile)

        # === Update admin dashboard stats ===
        stats = db_session.exec(select(AdminDashboardStats)).first()
        if not stats:
            stats = AdminDashboardStats()
            db_session.add(stats)
        stats.total_trainings = (stats.total_trainings or 0) + 1
        db_session.commit()

    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    return session


# Endpoint to delete all sessions for a user
@router.delete('/clear-all', response_model=dict)
def delete_sessions_by_user(
    db_session: Annotated[DBSession, Depends(get_db_session)],
    user_profile: Annotated[UserProfile, Depends(require_user)],
) -> dict:
    """
    Delete all sessions related to conversation scenarios for a given user ID.
    """
    logging.info(f'Deleting all sessions for user ID: {user_profile.id}')
    user_id = user_profile.id
    # Retrieve all conversation scenarios for the given user ID
    statement = select(ConversationScenario).where(ConversationScenario.user_id == user_id)
    conversation_scenarios = db_session.exec(statement).all()
    if not conversation_scenarios:
        raise HTTPException(status_code=404, detail='No sessions found for the given user ID')
    count_of_deleted_sessions = 0
    audios = []
    # Print all audio_uri values from SessionTurn for each session
    for conversation_scenario in conversation_scenarios:
        count_of_deleted_sessions += len(conversation_scenario.sessions)
        for session in conversation_scenario.sessions:
            for session_turn in session.session_turns:
                audios.append(session_turn.audio_uri)
            db_session.delete(session)
        db_session.commit()

    return {
        'message': f'Deleted {count_of_deleted_sessions} sessions for user ID {user_id}',
        'audios': audios,
    }


# Endpoint to delete a specific session by ID
@router.delete('/{session_id}', response_model=dict)
def delete_session(
    session_id: UUID, db_session: Annotated[DBSession, Depends(get_db_session)]
) -> dict:
    """
    Delete a session.
    """
    logging.info(f'Deleting session with ID: {session_id}')
    session = db_session.exec(select(Session).where(Session.id == session_id)).first()
    if not session:
        raise HTTPException(status_code=404, detail='Session not found')
    db_session.delete(session)
    db_session.commit()
    return {'message': 'Session deleted successfully'}
