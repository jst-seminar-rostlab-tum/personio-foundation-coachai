from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session as DBSession

from app.database import get_db_session
from app.dependencies import require_session
from app.models.session import Session
from app.services.realtime_session_service import RealtimeSessionService

router = APIRouter(prefix='/realtime-sessions', tags=['realtime-session'])


def get_realtime_session_service(
    db_session: Annotated[DBSession, Depends(get_db_session)],
) -> RealtimeSessionService:
    """
    Dependency factory to inject the RealtimeSessionService.
    """
    return RealtimeSessionService(db_session)


@router.get('/{session_id}')
async def get_realtime_session(
    service: Annotated[RealtimeSessionService, Depends(get_realtime_session_service)],
    session: Annotated[Session, Depends(require_session)],
) -> dict:
    """
    Proxies a POST request to OpenAI's realtime sessions endpoint
    and returns the JSON response.
    """
    return await service.get_realtime_session(session)
