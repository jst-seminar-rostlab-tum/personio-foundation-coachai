from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel import Session as DBSession

from app.database import get_db_session
from app.dependencies import require_user
from app.schemas.live_feedback_schema import LiveFeedbackRead
from app.services.live_feedback_service import LiveFeedbackService

router = APIRouter(
    prefix='/live-feedback',
    tags=['Live Feedback'],
    dependencies=[Depends(require_user)],
)


def get_live_feedback_service(
    db_session: Annotated[DBSession, Depends(get_db_session)],
) -> LiveFeedbackService:
    return LiveFeedbackService(db_session)


@router.get('/session/{session_id}', response_model=list[LiveFeedbackRead])
def get_feedback_for_session(
    session_id: UUID,
    service: Annotated[LiveFeedbackService, Depends(get_live_feedback_service)],
) -> list[LiveFeedbackRead]:
    return service.fetch_all_for_session(session_id)
