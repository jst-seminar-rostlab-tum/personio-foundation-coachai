from fastapi import HTTPException
from sqlmodel import Session as DBSession

from app.models.session import Session as SessionModel
from app.models.session_turn import SessionTurn
from app.schemas.session_turn import SessionTurnCreate, SessionTurnRead


class SessionTurnService:
    def __init__(self, db: DBSession) -> None:
        self.db = db

    def create_session_turn(self, turn: SessionTurnCreate) -> SessionTurnRead:
        """
        Create a new session turn.
        """
        # Validate foreign key
        session = self.db.get(SessionModel, turn.session_id)
        if not session:
            raise HTTPException(status_code=404, detail='Session not found')

        new_turn = SessionTurn(**turn.dict())
        self.db.add(new_turn)
        self.db.commit()
        self.db.refresh(new_turn)
        return SessionTurnRead.from_orm(new_turn)
