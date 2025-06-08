from math import ceil
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlmodel import Session as DBSession
from sqlmodel import col, select

from app.database import get_session
from app.models.conversation_turn import ConversationTurn
from app.models.language import Language
from app.models.training_case import TrainingCase
from app.models.training_session import (
    TrainingSession,
    TrainingSessionCreate,
    TrainingSessionDetailsRead,
    TrainingSessionRead,
)
from app.models.training_session_feedback import (
    TrainingSessionFeedback,
    TrainingSessionFeedbackMetrics,
    TrainingSessionFeedbackRead,
)
from app.models.training_sessions_paginated import (
    PaginatedTrainingSessionsResponse,
    SkillScores,
    TrainingSessionItem,
)

router = APIRouter(prefix='/training-session', tags=['Training Sessions'])


@router.get('/{id_training_session}', response_model=TrainingSessionDetailsRead)
def get_training_session(
    id_training_session: UUID, db_session: Annotated[DBSession, Depends(get_session)]
) -> TrainingSessionDetailsRead:
    """
    Retrieve a training session by its ID.
    """
    training_session = db_session.get(TrainingSession, id_training_session)
    if not training_session:
        raise HTTPException(status_code=404, detail='No session found with the given ID')

    # Get training session title from the training case
    training_case = db_session.get(TrainingCase, training_session.case_id)
    if training_case:
        if training_case.category:
            training_title = training_case.category.name
        else:
            training_title = training_case.custom_category_label
    else:
        training_title = 'Unknown'

    training_session_response = TrainingSessionDetailsRead(
        id=training_session.id,
        case_id=training_session.case_id,
        scheduled_at=training_session.scheduled_at,
        started_at=training_session.started_at,
        ended_at=training_session.ended_at,
        language_code=training_session.language_code,
        ai_persona=training_session.ai_persona,
        created_at=training_session.created_at,
        updated_at=training_session.updated_at,
        title=training_title,
        summary=(
            'The person giving feedback was rude but the person receiving feedback took it well.'
        ),  # mocked
    )

    # Fetch the asociated Feedback for the training session
    feedback = db_session.exec(
        select(TrainingSessionFeedback).where(
            TrainingSessionFeedback.session_id == id_training_session
        )
    ).first()
    if feedback:
        training_session_response.feedback = TrainingSessionFeedbackMetrics(
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
    conversation_turns = db_session.exec(
        select(ConversationTurn).where(ConversationTurn.session_id == id_training_session)
    ).all()
    if conversation_turns:
        training_session_response.audio_uris = [turn.audio_uri for turn in conversation_turns]

    return training_session_response


@router.get('/{id_training_session}/feedback', response_model=TrainingSessionFeedbackRead)
def get_training_session_feedback(
    id_training_session: UUID, db_session: Annotated[DBSession, Depends(get_session)]
) -> TrainingSessionFeedback:
    """
    Retrieve the training session feedback for a given training session ID.
    """
    # Validate that the training session exists
    training_session = db_session.get(TrainingSession, id_training_session)
    if not training_session:
        raise HTTPException(status_code=404, detail='Training session not found')

    # Fetch the associated training session feedback
    statement = select(TrainingSessionFeedback).where(
        TrainingSessionFeedback.session_id == id_training_session
    )
    training_session_feedback = db_session.exec(statement).first()

    if not training_session_feedback:
        raise HTTPException(status_code=404, detail='Training session feedback not found')

    return training_session_feedback


@router.get('/', response_model=PaginatedTrainingSessionsResponse)
def get_training_sessions(
    db_session: Annotated[DBSession, Depends(get_session)],
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    x_user_id: str = Header(...),  # Auth via header
    # TODO: Adjust to the authentication token in the header
) -> PaginatedTrainingSessionsResponse:
    """
    Return paginated list of completed training sessions for a user.
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
        return PaginatedTrainingSessionsResponse(
            page=page,
            limit=page_size,
            total_pages=0,
            total_sessions=0,
            sessions=[],
        )

    # Query sessions
    session_query = (
        select(TrainingSession)
        .where(col(TrainingSession.case_id).in_(training_case_ids))
        .order_by(col(TrainingSession.ended_at).desc())
    )

    total_sessions = len(db_session.exec(session_query).all())
    sessions = db_session.exec(session_query.offset((page - 1) * page_size).limit(page_size)).all()

    session_list = [
        TrainingSessionItem(
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

    return PaginatedTrainingSessionsResponse(
        page=page,
        limit=page_size,
        total_pages=ceil(total_sessions / page_size),
        total_sessions=total_sessions,
        sessions=session_list,
    )


@router.post('/', response_model=TrainingSessionRead)
def create_training_session(
    session_data: TrainingSessionCreate, db_session: Annotated[DBSession, Depends(get_session)]
) -> TrainingSession:
    """
    Create a new training session.
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

    new_training_session = TrainingSession(**session_data.dict())
    db_session.add(new_training_session)
    db_session.commit()
    db_session.refresh(new_training_session)
    return new_training_session


@router.put('/{session_id}', response_model=TrainingSessionRead)
def update_training_session(
    session_id: UUID,
    updated_data: TrainingSessionCreate,
    db_session: Annotated[DBSession, Depends(get_session)],
) -> TrainingSession:
    """
    Update an existing training session.
    """
    training_session = db_session.get(TrainingSession, session_id)
    if not training_session:
        raise HTTPException(status_code=404, detail='Training session not found')

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
        setattr(training_session, key, value)

    db_session.add(training_session)
    db_session.commit()
    db_session.refresh(training_session)
    return training_session


@router.delete('/{session_id}', response_model=dict)
def delete_training_session(
    session_id: UUID, db_session: Annotated[DBSession, Depends(get_session)]
) -> dict:
    """
    Delete a training session.
    """
    training_session = db_session.get(TrainingSession, session_id)
    if not training_session:
        raise HTTPException(status_code=404, detail='Training session not found')

    db_session.delete(training_session)
    db_session.commit()
    return {'message': 'Training session deleted successfully'}


@router.delete('/clear-all/{user_id}', response_model=dict)
def delete_training_sessions_by_user(
    user_id: UUID, db_session: Annotated[DBSession, Depends(get_session)]
) -> dict:
    """
    Delete all training sessions related to training cases for a given user ID.
    """
    # Retrieve all training cases for the given user ID
    statement = select(TrainingCase).where(TrainingCase.user_id == user_id)
    training_cases = db_session.exec(statement).all()
    print(f'Training cases for user ID {user_id}: {training_cases}')
    if not training_cases:
        raise HTTPException(
            status_code=404, detail='No training sessions found for the given user ID'
        )
    count_of_deleted_training_sessions = 0
    audios = []
    # Print all audio_uri values from ConversationTurn for each training session
    for training_case in training_cases:
        count_of_deleted_training_sessions += len(training_case.sessions)

        for training_session in training_case.sessions:
            for conversation_turn in training_session.conversation_turns:
                audios.append(conversation_turn.audio_uri)
            db_session.delete(training_session)

    db_session.commit()

    return {
        'message': f'Deleted {count_of_deleted_training_sessions} sessions for user ID {user_id}',
        'audios': audios,
    }
