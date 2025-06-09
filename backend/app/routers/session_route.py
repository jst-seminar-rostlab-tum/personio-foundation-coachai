from math import ceil
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlmodel import Session as DBSession
from sqlmodel import col, select

from app.database import get_session as get_db_session
from app.models.language import Language
from app.models.session import (
    Session,
    SessionCreate,
    SessionDetailsRead,
    SessionRead,
)
from app.models.session_feedback import (
    SessionFeedback,
    SessionFeedbackMetrics,
    SessionFeedbackRead,
)
from app.models.session_turn import SessionTurn
from app.models.sessions_paginated import (
    PaginatedSessionsResponse,
    SessionItem,
    SkillScores,
)
from app.models.training_case import TrainingCase

router = APIRouter(prefix='/session', tags=['Sessions'])


@router.get('/{session_id}', response_model=SessionDetailsRead)
def get_session_by_id(
    session_id: UUID, db_session: Annotated[DBSession, Depends(get_db_session)]
) -> SessionDetailsRead:
    """
    Retrieve a session by its ID.
    """
    session = db_session.get(Session, session_id)
    if not session:
        raise HTTPException(status_code=404, detail='No session found with the given ID')

    # Get session title from the training case
    training_case = db_session.get(TrainingCase, session.case_id)
    if training_case:
        if training_case.category:
            training_title = training_case.category.name
        else:
            training_title = training_case.custom_category_label
    else:
        training_title = 'Unknown'

    session_response = SessionDetailsRead(
        id=session.id,
        case_id=session.case_id,
        scheduled_at=session.scheduled_at,
        started_at=session.started_at,
        ended_at=session.ended_at,
        language_code=session.language_code,
        ai_persona=session.ai_persona,
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
    if feedback:
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


@router.get('/{session_id}/feedback', response_model=SessionFeedbackRead)
def get_session_feedback(
    session_id: UUID, db_session: Annotated[DBSession, Depends(get_db_session)]
) -> SessionFeedback:
    """
    Retrieve the session feedback for a given session ID.
    """
    # Validate that the session exists
    session = db_session.get(Session, session_id)
    if not session:
        raise HTTPException(status_code=404, detail='Session not found')

    # Fetch the associated session feedback
    statement = select(SessionFeedback).where(SessionFeedback.session_id == session_id)
    session_feedback = db_session.exec(statement).first()

    if not session_feedback:
        raise HTTPException(status_code=404, detail='Session feedback not found')

    return session_feedback


@router.get('/', response_model=PaginatedSessionsResponse)
def get_sessions(
    db_session: Annotated[DBSession, Depends(get_db_session)],
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    x_user_id: str = Header(...),  # Auth via header
    # TODO: Adjust to the authentication token in the header
) -> PaginatedSessionsResponse:
    """
    Return paginated list of completed sessions for a user.
    """
    # Get all training cases for the user
    try:
        user_id = UUID(x_user_id)
    except ValueError as err:
        raise HTTPException(
            status_code=401, detail='Invalid or missing authentication token'
        ) from err

    statement = select(TrainingCase.id).where(TrainingCase.user_id == user_id)
    training_case_ids = db_session.exec(statement).all()

    if not training_case_ids:
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
        .where(col(Session.case_id).in_(training_case_ids))
        .order_by(col(Session.ended_at).desc())
    )

    total_sessions = len(db_session.exec(session_query).all())
    sessions = db_session.exec(session_query.offset((page - 1) * page_size).limit(page_size)).all()

    session_list = [
        SessionItem(
            session_id=sess.id,
            title='Negotiating Job Offers',  # mocked
            summary='Practice salary negotiation with a potential candidate',  # mocked
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


@router.post('/', response_model=SessionRead)
def create_session(
    session_data: SessionCreate, db_session: Annotated[DBSession, Depends(get_db_session)]
) -> Session:
    """
    Create a new session.
    """
    # Validate foreign keys
    case = db_session.get(TrainingCase, session_data.case_id)
    if not case:
        raise HTTPException(status_code=404, detail='Training case not found')

    language = db_session.exec(
        select(Language).where(Language.code == session_data.language_code)
    ).first()
    if not language:
        raise HTTPException(status_code=404, detail='Language not found')

    new_session = Session(**session_data.dict())
    db_session.add(new_session)
    db_session.commit()
    db_session.refresh(new_session)
    return new_session


@router.put('/{session_id}', response_model=SessionRead)
def update_session(
    session_id: UUID,
    updated_data: SessionCreate,
    db_session: Annotated[DBSession, Depends(get_db_session)],
) -> Session:
    """
    Update an existing session.
    """
    session = db_session.get(Session, session_id)
    if not session:
        raise HTTPException(status_code=404, detail='Session not found')

    # Validate foreign keys
    if updated_data.case_id:
        case = db_session.get(TrainingCase, updated_data.case_id)
        if not case:
            raise HTTPException(status_code=404, detail='Training case not found')

    if updated_data.language_code:
        language = db_session.exec(
            select(Language).where(Language.code == updated_data.language_code)
        ).first()
        if not language:
            raise HTTPException(status_code=404, detail='Language not found')

    for key, value in updated_data.dict().items():
        setattr(session, key, value)

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


@router.delete('/clear-all/{user_id}', response_model=dict)
def delete_sessions_by_user(
    user_id: UUID, db_session: Annotated[DBSession, Depends(get_db_session)]
) -> dict:
    """
    Delete all sessions related to training cases for a given user ID.
    """
    # Retrieve all training cases for the given user ID
    statement = select(TrainingCase).where(TrainingCase.user_id == user_id)
    training_cases = db_session.exec(statement).all()
    print(f'Training cases for user ID {user_id}: {training_cases}')
    if not training_cases:
        raise HTTPException(status_code=404, detail='No sessions found for the given user ID')
    count_of_deleted_sessions = 0
    audios = []
    # Print all audio_uri values from SessionTurn for each session
    for training_case in training_cases:
        count_of_deleted_sessions += len(training_case.sessions)

        for session in training_case.sessions:
            for session_turn in session.session_turns:
                audios.append(session_turn.audio_uri)
            db_session.delete(session)

    db_session.commit()

    return {
        'message': f'Deleted {count_of_deleted_sessions} sessions for user ID {user_id}',
        'audios': audios,
    }
