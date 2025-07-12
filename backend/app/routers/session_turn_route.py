from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, UploadFile
from sqlmodel import Session as DBSession

from app.database import get_db_session
from app.dependencies import require_user
from app.models.session_turn import SpeakerEnum
from app.models.user_profile import UserProfile
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
async def create_session_turn(
    service: Annotated[SessionTurnService, Depends(get_session_turn_service)],
    user_profile: Annotated[UserProfile, Depends(require_user)],
    background_tasks: BackgroundTasks,
    session_id: UUID = Form(...),  # noqa: B008
    speaker: SpeakerEnum = Form(...),  # noqa: B008
    start_offset_ms: int = Form(...),  # noqa: B008
    end_offset_ms: int = Form(...),  # noqa: B008
    text: str = Form(...),  # noqa: B008
    audio_file: UploadFile = File(...),  # noqa: B008
) -> SessionTurnRead:
    # manually create SessionTurnCreate
    turn = SessionTurnCreate(
        session_id=session_id,
        speaker=speaker,
        start_offset_ms=start_offset_ms,
        end_offset_ms=end_offset_ms,
        text=text,
    )

    return await service.create_session_turn(turn, audio_file, user_profile, background_tasks)
