from math import ceil
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlmodel import Session as DBSession
from sqlmodel import col, select

from app.database import get_db_session
from app.dependencies import require_user
from app.models.conversation_category import ConversationCategory
from app.models.conversation_scenario import ConversationScenario
from app.models.scenario_preparation import ScenarioPreparation, ScenarioPreparationStatus
from app.models.session import (
    Session,
    SessionCreate,
    SessionDetailsRead,
    SessionRead,
    SessionStatus,
    SessionUpdate,
)
from app.models.session_feedback import (
    FeedbackStatusEnum,
    SessionFeedback,
    SessionFeedbackMetrics,
)
from app.models.session_turn import SessionTurn
from app.models.sessions_paginated import (
    PaginatedSessionsResponse,
    SessionItem,
    SkillScores,
)
from app.models.user_profile import AccountRole, UserProfile
from app.schemas.session_feedback_schema import ExamplesRequest
from app.services.session_feedback_service import generate_and_store_feedback

router = APIRouter(prefix='/session', tags=['Sessions'])


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

    current_scenario = session.scenario
    if current_scenario.user_id != user_profile.id and user_profile.account_role != 'admin':
        raise HTTPException(
            status_code=400,
            detail='You do not have permission to access this session '
            'you can only view your own sessions',
        )
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
    else:
        training_title = conversation_scenario.custom_category_label

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
    )

    # Fetch the asociated Feedback for the session
    feedback = db_session.exec(
        select(SessionFeedback).where(SessionFeedback.session_id == session_id)
    ).first()

    if not feedback:
        raise HTTPException(status_code=404, detail='Session feedback not found')

    if feedback.status == FeedbackStatusEnum.pending:
        raise HTTPException(status_code=202, detail='Session feedback in progress.')
    elif feedback.status == FeedbackStatusEnum.failed:
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

    # Fetch the associated conversation turns and their audio URIs
    session_turns = db_session.exec(
        select(SessionTurn).where(SessionTurn.session_id == session_id)
    ).all()

    if session_turns:
        session_response.audio_uris = [turn.audio_uri for turn in session_turns]

    return session_response


@router.get('/', response_model=PaginatedSessionsResponse)
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
        .order_by(col(Session.ended_at).desc())
    )

    total_sessions = len(db_session.exec(session_query).all())
    sessions = db_session.exec(session_query.offset((page - 1) * page_size).limit(page_size)).all()

    session_list = [
        SessionItem(
            session_id=sess.id,
            title='Negotiating Job Offers',  # mocked
            summary='Practice salary negotiation with a potential candidate',  # mocked
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
        for sess in sessions
    ]

    return PaginatedSessionsResponse(
        page=page,
        limit=page_size,
        total_pages=ceil(total_sessions / page_size),
        total_sessions=total_sessions,
        sessions=session_list,
    )


@router.post('/', response_model=SessionRead, dependencies=[Depends(require_user)])
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

    db_session.add(new_session)
    db_session.commit()
    db_session.refresh(new_session)
    return new_session


@router.put('/{session_id}', response_model=SessionRead)
def update_session(
    session_id: UUID,
    updated_data: SessionUpdate,
    db_session: Annotated[DBSession, Depends(get_db_session)],
    background_tasks: BackgroundTasks,
) -> Session:
    """
    Update an existing session.
    """
    session = db_session.get(Session, session_id)
    if not session:
        raise HTTPException(status_code=404, detail='Session not found')

    previous_status = session.status
    conversation_scenario = None

    scenario_id = updated_data.scenario_id or session.scenario_id

    # Validate foreign keys
    if scenario_id:
        conversation_scenario = db_session.get(ConversationScenario, scenario_id)
        if not conversation_scenario:
            raise HTTPException(status_code=404, detail='Conversation scenario not found')

    for key, value in updated_data.model_dump(exclude_unset=True).items():
        setattr(session, key, value)

    print(f'Session feedback: {session.feedback is not None}')
    # Check if the session status is changing to completed
    if (
        previous_status != SessionStatus.completed
        and updated_data.status == SessionStatus.completed
        and session.feedback is None
    ):
        if not scenario_id:
            raise HTTPException(
                status_code=500,
                detail='Conversation scenario must be provided to generate feedback',
            )

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

        print(f'Generating feedback for session {session.id} with transcripts: {transcripts}')

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
        )

        # Schedule the feedback generation in the background
        background_tasks.add_task(
            generate_and_store_feedback,
            session_id=session.id,
            example_request=request,
            db_session=db_session,
        )

    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    return session


@router.delete('/{session_id}', response_model=dict)
def delete_session(
    session_id: UUID, db_session: Annotated[DBSession, Depends(get_db_session)]
) -> dict:
    """
    Delete a session.
    """
    session = db_session.get(Session, session_id)
    if not session:
        raise HTTPException(status_code=404, detail='Session not found')

    db_session.delete(session)
    db_session.commit()
    return {'message': 'Session deleted successfully'}


@router.delete('/clear-all', response_model=dict)
def delete_sessions_by_user(
    db_session: Annotated[DBSession, Depends(get_db_session)],
    user: Annotated[UserProfile, Depends(require_user)],
) -> dict:
    """
    Delete all sessions related to conversation scenarios for a given user ID.
    """
    user_id = user.id
    # Retrieve all conversation scenarios for the given user ID
    statement = select(ConversationScenario).where(ConversationScenario.user_id == user_id)
    conversation_scenarios = db_session.exec(statement).all()
    print(f'Conversation scenarios for user ID {user_id}: {conversation_scenarios}')
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
