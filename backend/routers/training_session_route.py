from math import ceil
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlmodel import Session, col, select

from ..database import get_session
from ..models.language import Language
from ..models.training_case import TrainingCase
from ..models.training_session import (
    TrainingSession,
    TrainingSessionCreate,
    TrainingSessionRead,
)
from ..models.training_session_feedback import (
    TrainingSessionFeedback,
    TrainingSessionFeedbackRead,
)
from ..models.training_sessions_paginated import (
    PaginatedTrainingSessionsResponse,
    SkillScores,
    TrainingSessionItem,
)

router = APIRouter(prefix='/training-session', tags=['Training Sessions'])


@router.get('/{id_training_session}/feedback', response_model=TrainingSessionFeedbackRead)
def get_training_session_feedback(
    id_training_session: UUID, session: Annotated[Session, Depends(get_session)]
) -> TrainingSessionFeedback:
    """
    Retrieve the training session feedback for a given training session ID.
    """
    # Validate that the training session exists
    training_session = session.get(TrainingSession, id_training_session)
    if not training_session:
        raise HTTPException(status_code=404, detail='Training session not found')

    # Fetch the associated training session feedback
    statement = select(TrainingSessionFeedback).where(
        TrainingSessionFeedback.session_id == id_training_session
    )
    training_session_feedback = session.exec(statement).first()

    if not training_session_feedback:
        raise HTTPException(status_code=404, detail='Training session feedback not found')

    return training_session_feedback


@router.get('/', response_model=PaginatedTrainingSessionsResponse)
def get_training_sessions(
    session: Annotated[Session, Depends(get_session)],
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
    training_case_ids = session.exec(statement).all()

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

    total_sessions = len(session.exec(session_query).all())
    sessions = session.exec(session_query.offset((page - 1) * page_size).limit(page_size)).all()

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
    session_data: TrainingSessionCreate, session: Annotated[Session, Depends(get_session)]
) -> TrainingSession:
    """
    Create a new training session.
    """
    # Validate foreign keys
    case = session.get(TrainingCase, session_data.case_id)
    if not case:
        raise HTTPException(status_code=404, detail='Training case not found')

    language = session.exec(
        select(Language).where(Language.code == session_data.language_code)
    ).first()
    if not language:
        raise HTTPException(status_code=404, detail='Language not found')

    db_session = TrainingSession(**session_data.dict())
    session.add(db_session)
    session.commit()
    session.refresh(db_session)
    return db_session


@router.put('/{session_id}', response_model=TrainingSessionRead)
def update_training_session(
    session_id: UUID,
    updated_data: TrainingSessionCreate,
    session: Annotated[Session, Depends(get_session)],
) -> TrainingSession:
    """
    Update an existing training session.
    """
    training_session = session.get(TrainingSession, session_id)
    if not training_session:
        raise HTTPException(status_code=404, detail='Training session not found')

    # Validate foreign keys
    if updated_data.case_id:
        case = session.get(TrainingCase, updated_data.case_id)
        if not case:
            raise HTTPException(status_code=404, detail='Training case not found')

    if updated_data.language_code:
        language = session.exec(
            select(Language).where(Language.code == updated_data.language_code)
        ).first()
        if not language:
            raise HTTPException(status_code=404, detail='Language not found')

    for key, value in updated_data.dict().items():
        setattr(training_session, key, value)

    session.add(training_session)
    session.commit()
    session.refresh(training_session)
    return training_session


@router.delete('/{session_id}', response_model=dict)
def delete_training_session(
    session_id: UUID, session: Annotated[Session, Depends(get_session)]
) -> dict:
    """
    Delete a training session.
    """
    training_session = session.get(TrainingSession, session_id)
    if not training_session:
        raise HTTPException(status_code=404, detail='Training session not found')

    session.delete(training_session)
    session.commit()
    return {'message': 'Training session deleted successfully'}


@router.delete('/clear-all/{user_id}', response_model=dict)
def delete_training_sessions_by_user(
    user_id: UUID, session: Annotated[Session, Depends(get_session)]
) -> dict:
    """
    Delete all training sessions related to training cases for a given user ID.
    """
    # Retrieve all training cases for the given user ID
    statement = select(TrainingCase).where(TrainingCase.user_id == user_id)
    training_cases = session.exec(statement).all()
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
            session.delete(training_session)

    session.commit()

    return {
        'message': f'Deleted {count_of_deleted_training_sessions} sessions for user ID {user_id}',
        'audios': audios,
    }
