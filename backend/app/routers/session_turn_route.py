from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session as DBSession

from app.database import get_db_session
from app.dependencies import require_user
from app.schemas.session_turn import SessionTurnCreate, SessionTurnRead
from app.services.session_turn_service import create_new_session_turn

router = APIRouter(
    prefix='/session-turns', tags=['Session Turns'], dependencies=[Depends(require_user)]
)


@router.post('', response_model=SessionTurnRead)
def create_session_turn(
    turn: SessionTurnCreate, db_session: Annotated[DBSession, Depends(get_db_session)]
) -> SessionTurnRead:
    """
    Create a new session turn.
    """
    return create_new_session_turn(turn, db_session)
