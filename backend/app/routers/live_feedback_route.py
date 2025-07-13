from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session as DBSession

from app.database import get_db_session
from app.dependencies import require_session, require_user
from app.models.session import Session
from app.schemas.live_feedback_schema import LiveFeedbackRead
from app.services.live_feedback_service import fetch_live_feedback_for_session

router = APIRouter(
    prefix='/live-feedback',
    tags=['Live Feedback'],
    dependencies=[Depends(require_user)],
)


@router.get('/session/{session_id}', response_model=list[LiveFeedbackRead])
def get_live_feedback_for_session(
    db_session: Annotated[DBSession, Depends(get_db_session)],
    session: Annotated[Session, Depends(require_session)],
    limit: Optional[int] = Query(None, gt=0),
) -> list[LiveFeedbackRead]:
    return fetch_live_feedback_for_session(db_session, session.id, limit)
