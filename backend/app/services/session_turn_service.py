from fastapi import BackgroundTasks, HTTPException
from sqlmodel import Session as DBSession

from app.models.session import Session as SessionModel
from app.models.session_turn import SessionTurn
from app.schemas.session_turn import SessionTurnCreate, SessionTurnRead
from app.services.live_feedback_service import generate_and_store_live_feedback


class SessionTurnService:
    def __init__(self, db: DBSession) -> None:
        self.db = db

    def create_session_turn(
        self,
        turn: SessionTurnCreate,
        background_tasks: BackgroundTasks,
    ) -> SessionTurnRead:
        """
        Create a new session turn.
        """
        # Validate foreign key
        session = self.db.get(SessionModel, turn.session_id)
        if not session:
            raise HTTPException(status_code=404, detail='Session not found')

        new_turn = SessionTurn(**turn.model_dump())
        self.db.add(new_turn)
        self.db.commit()
        self.db.refresh(new_turn)

        background_tasks.add_task(
            generate_and_store_live_feedback,
            db_session=self.db,
            session_id=turn.session_id,
            session_turn_context=turn,
        )

        return SessionTurnRead(**new_turn.model_dump())
