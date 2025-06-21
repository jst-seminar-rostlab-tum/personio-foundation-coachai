from fastapi import HTTPException
from sqlmodel import Session

from app.models.session import Session as SessionModel
from app.models.session_turn import SessionTurn
from app.schemas.session_turn import SessionTurnCreate, SessionTurnRead


def create_new_session_turn(turn: SessionTurnCreate, db_session: Session) -> SessionTurnRead:
    """
    Create a new session turn.
    """
    # Validate foreign key
    session = db_session.get(SessionModel, turn.session_id)
    if not session:
        raise HTTPException(status_code=404, detail='Session not found')

    new_turn = SessionTurn(**turn.dict())
    db_session.add(new_turn)
    db_session.commit()
    db_session.refresh(new_turn)
    return SessionTurnRead.from_orm(new_turn)
