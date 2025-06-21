from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session as DBSession

from app.database import get_db_session
from app.dependencies import require_user
from app.schemas.session_turn import SessionTurnCreate, SessionTurnRead
from app.services.session_turn_service import SessionTurnService

router = APIRouter(
    prefix='/session-turns', tags=['Session Turns'], dependencies=[Depends(require_user)]
)


def get_session_turn_service(
    db_session: Annotated[DBSession, Depends(get_db_session)],
) -> SessionTurnService:
    """
    Dependency factory to inject the SessionTurnService.
    """
    return SessionTurnService(db_session)


@router.post('', response_model=SessionTurnRead)
def create_session_turn(
    turn: SessionTurnCreate,
    service: Annotated[SessionTurnService, Depends(get_session_turn_service)],
) -> SessionTurnRead:
    """
    Create a new session turn.
    """
    return service.create_session_turn(turn)
