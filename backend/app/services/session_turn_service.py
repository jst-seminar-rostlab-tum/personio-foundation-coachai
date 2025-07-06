from uuid import uuid4

import puremagic
from fastapi import HTTPException, UploadFile, BackgroundTasks
from sqlalchemy import UUID
from sqlmodel import Session as DBSession

from app.config import Settings
from app.connections.gcs_client import get_gcs_audio_manager
from app.models.session import Session as SessionModel
from app.models.session_turn import SessionTurn, SpeakerEnum
from app.schemas.session_turn import SessionTurnCreate, SessionTurnRead
from app.services.live_feedback_service import generate_and_store_live_feedback

settings = Settings()


def is_valid_audio_mime_type(mime_type: str) -> bool:
    return mime_type in [
        'audio/webm',
        'video/webm',
        'audio/mpeg',
        'video/mpeg',
        'audio/wav',
        'audio/x-wav',
        'audio/wave',
    ]


def get_audio_content_type(upload_file: UploadFile) -> str:
    matches = puremagic.magic_stream(upload_file.file)
    upload_file.file.seek(0)

    if not matches:
        raise HTTPException(status_code=400, detail='Only .webm, .mp3 or .wav files are allowed')

    mime = matches[0].mime_type

    if not is_valid_audio_mime_type(mime):
        raise HTTPException(status_code=400, detail='Only .webm, .mp3 or .wav files are allowed')

    return mime


def store_audio_file(session_id: UUID, audio_file: UploadFile) -> str:
    audio_name = f'{session_id}_{uuid4().hex}'
    gcs = get_gcs_audio_manager()

    if gcs is None:
        raise HTTPException(status_code=500, detail='Failed to connect to audio storage')

    try:
        gcs.upload_from_fileobj(
            file_obj=audio_file.file,
            blob_name=audio_name,
            content_type=get_audio_content_type(audio_file),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail='Failed to upload audio file') from e

    return audio_name


class SessionTurnService:
    def __init__(self, db: DBSession) -> None:
        self.db = db


    async def create_session_turn(
        self,
        turn: SessionTurnCreate,
        audio_file: UploadFile,
        background_tasks: BackgroundTasks,
    ) -> SessionTurnRead:
        """
        Create a new session turn.
        """
        # Validate foreign key
        session = self.db.get(SessionModel, turn.session_id)
        if not session:
            raise HTTPException(status_code=404, detail='Session not found')

        # Validate required fields
        if not turn.text:
            raise HTTPException(status_code=400, detail='Text is required')

        audio_uri = ''
        if settings.ENABLE_AI:
            audio_uri = store_audio_file(turn.session_id, audio_file)

        # Create a new SessionTurn instance
        turn_data = turn.model_dump()
        turn_data['audio_uri'] = audio_uri
        new_turn = SessionTurn(**turn_data)

        self.db.add(new_turn)
        self.db.commit()
        self.db.refresh(new_turn)

        if turn.speaker == SpeakerEnum.user:
            # Generate live feedback item in the background
            background_tasks.add_task(
                generate_and_store_live_feedback,
                db_session=self.db,
                session_id=turn.session_id,
                session_turn_context=turn,
            )

        return SessionTurnRead(
            id=new_turn.id,
            session_id=new_turn.session_id,
            speaker=new_turn.speaker,
            start_offset_ms=new_turn.start_offset_ms,
            end_offset_ms=new_turn.end_offset_ms,
            text=new_turn.text,
            audio_uri=audio_uri,
            ai_emotion=new_turn.ai_emotion,
            created_at=new_turn.created_at,
        )
