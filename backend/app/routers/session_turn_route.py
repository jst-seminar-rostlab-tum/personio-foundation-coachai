from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlmodel import Session as DBSession

from app.database import get_db_session
from app.dependencies import require_user
from app.models.session_turn import SpeakerEnum
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

    return await service.create_session_turn(turn, audio_file)


@router.get('/{session_id}/stitch', response_model=tuple[str | None, list[float]])
async def stitch_session_turns(
    service: Annotated[SessionTurnService, Depends(get_session_turn_service)],
    session_id: UUID,
) -> tuple[str | None, list[float]]:
    """
    Stitch all audio files of a session into a single audio file.
    """
    a, b = await service.stitch_mp3s_from_gcs(session_id, f'{session_id}')
    return (a, b)
