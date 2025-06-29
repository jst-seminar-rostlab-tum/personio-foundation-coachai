from typing import Annotated
from uuid import UUID, uuid4

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

session_id_form = Form(...)
speaker_form = Form(...)
start_offset_ms_form = Form(...)
end_offset_ms_form = Form(...)
text_form = Form(...)
ai_emotion_form = Form(...)
audio_file_file = File(...)


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
    session_id: UUID = session_id_form,
    speaker: SpeakerEnum = speaker_form,
    start_offset_ms: int = start_offset_ms_form,
    end_offset_ms: int = end_offset_ms_form,
    text: str = text_form,
    ai_emotion: str = ai_emotion_form,
    audio_file: UploadFile = audio_file_file,
) -> SessionTurnRead:
    # Generate a unique audio name using session_id and uuid
    audio_name = f'{session_id}_{uuid4().hex}.mp3'

    # manually create SessionTurnCreate
    turn = SessionTurnCreate(
        session_id=session_id,
        speaker=speaker,
        start_offset_ms=start_offset_ms,
        end_offset_ms=end_offset_ms,
        text=text,
        ai_emotion=ai_emotion,
        audio_name=audio_name,
    )

    return service.create_session_turn(turn, audio_file)
