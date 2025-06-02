from math import ceil
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlmodel import Session, select

from backend.database import get_session
from backend.models.training_case import TrainingCase
from backend.models.training_session import TrainingSession
from backend.models.training_sessions_paginated import (
    PaginatedTrainingSessionsResponse,
    SkillScores,
    TrainingSessionItem,
)

router = APIRouter(prefix='/training-sessions', tags=['Training History'])


@router.get('/', response_class=JSONResponse)
def get_paginated_training_sessions(
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
        .where(TrainingSession.case_id.in_(training_case_ids))
        .order_by(TrainingSession.ended_at.desc())
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
