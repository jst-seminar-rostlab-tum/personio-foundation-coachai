from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session as DBSession
from sqlmodel import select

from app.database import get_db_session
from app.dependencies import require_user
from app.models.session import Session
from app.models.user_profile import UserProfile
from app.schemas.live_feedback_schema import LiveFeedbackRead
from app.services.live_feedback_service import fetch_live_feedback_for_session

router = APIRouter(
    prefix='/live-feedback',
    tags=['Live Feedback'],
    dependencies=[Depends(require_user)],
)


@router.get('/session/{session_id}', response_model=list[LiveFeedbackRead])
def get_live_feedback_for_session(
    session_id: UUID,
    db_session: Annotated[DBSession, Depends(get_db_session)],
    user_profile: Annotated[UserProfile, Depends(require_user)],
    limit: Optional[int] = Query(None, gt=0),
) -> list[LiveFeedbackRead]:
    session = db_session.exec(select(Session).where(Session.id == session_id)).first()
    if not session.scenario.user_id == user_profile.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='User is not the owner of the scenario'
        )

    return fetch_live_feedback_for_session(db_session, session_id, limit)
