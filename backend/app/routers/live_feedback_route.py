from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel import Session as DBSession

from app.database import get_db_session
from app.dependencies import require_user
from app.schemas.live_feedback_schema import LiveFeedback
from app.services.live_feedback_service import fetch_all_for_session

router = APIRouter(
    prefix='/live-feedback',
    tags=['Live Feedback'],
    dependencies=[Depends(require_user)],
)


@router.get('/session/{session_id}', response_model=list[LiveFeedback])
def get_live_feedback_for_session(
    session_id: UUID,
    db_session: Annotated[DBSession, Depends(get_db_session)],
) -> list[LiveFeedback]:
    return fetch_all_for_session(db_session, session_id)
