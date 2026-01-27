"""API routes for session turn route."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, UploadFile
from sqlmodel import Session as DBSession

from app.dependencies.auth import require_user
from app.dependencies.database import get_db_session
from app.enums.speaker import SpeakerType
from app.models.user_profile import UserProfile
from app.schemas.session_turn import SessionTurnCreate, SessionTurnRead
from app.services.session_turn_service import SessionTurnService

router = APIRouter(
    prefix='/session-turns', tags=['Session Turns'], dependencies=[Depends(require_user)]
)


def get_session_turn_service(
    db_session: Annotated[DBSession, Depends(get_db_session)],
) -> SessionTurnService:
    """Provide SessionTurnService via dependency injection.

    Parameters:
        db_session (DBSession): Database session dependency.

    Returns:
        SessionTurnService: Service instance.
    """
    return SessionTurnService(db_session)


@router.post('', response_model=SessionTurnRead)
async def create_session_turn(
    service: Annotated[SessionTurnService, Depends(get_session_turn_service)],
    user_profile: Annotated[UserProfile, Depends(require_user)],
    background_tasks: BackgroundTasks,
    session_id: UUID = Form(...),  # noqa: B008
    speaker: SpeakerType = Form(...),  # noqa: B008
    start_offset_ms: int = Form(...),  # noqa: B008
    end_offset_ms: int = Form(...),  # noqa: B008
    text: str = Form(...),  # noqa: B008
    audio_file: UploadFile = File(...),  # noqa: B008
) -> SessionTurnRead:
    """Create a session turn with uploaded audio.

    Parameters:
        service (SessionTurnService): Service dependency.
        user_profile (UserProfile): Authenticated user profile.
        background_tasks (BackgroundTasks): Background task manager.
        session_id (UUID): Session identifier.
        speaker (SpeakerType): Speaker enum.
        start_offset_ms (int): Start offset in milliseconds.
        end_offset_ms (int): End offset in milliseconds.
        text (str): Transcript text.
        audio_file (UploadFile): Uploaded audio file.

    Returns:
        SessionTurnRead: Created turn payload.
    """
    # manually create SessionTurnCreate
    turn = SessionTurnCreate(
        session_id=session_id,
        speaker=speaker,
        start_offset_ms=start_offset_ms,
        end_offset_ms=end_offset_ms,
        text=text,
    )

    return await service.create_session_turn(turn, audio_file, user_profile, background_tasks)
