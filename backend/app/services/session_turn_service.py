import os
from uuid import uuid4

import puremagic
from fastapi import HTTPException, UploadFile
from sqlmodel import Session as DBSession

from app.models.session import Session as SessionModel
from app.models.session_turn import SessionTurn
from app.schemas.session_turn import SessionTurnCreate, SessionTurnRead
from app.services.google_cloud_storage_service import GCSManager


def is_valid_audio(upload_file: UploadFile) -> bool:
    matches = puremagic.magic_stream(upload_file.file)

    # Reset the file pointer to the beginning after reading
    upload_file.file.seek(0)

    if not matches:
        return False

    mime = matches[0].mime_type
    return mime in ['audio/webm', 'audio/mpeg', 'audio/wav']


def match_audio_content_type(file: UploadFile) -> tuple[str, str]:
    """
    Validate audio file extension and return (ext, content_type).
    """
    ext = os.path.splitext(file.filename)[-1].lower()
    if ext == '.webm':
        return ext, 'audio/webm'
    elif ext == '.mp3':
        return ext, 'audio/mpeg'
    elif ext == '.wav':
        return ext, 'audio/wav'
    else:
        raise HTTPException(status_code=400, detail='Only .webm, .mp3 or .wav files are allowed')


class SessionTurnService:
    def __init__(self, db: DBSession) -> None:
        self.db = db

    async def create_session_turn(
        self,
        turn: SessionTurnCreate,
        audio_file: UploadFile,
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

        # Check if the uploaded audio file is valid
        try:
            ext, content_type = match_audio_content_type(audio_file)
        except HTTPException as e:
            raise e

        if not is_valid_audio(audio_file):
            raise HTTPException(status_code=400, detail='Uploaded file is not a valid audio type')

        # Generate a unique audio name using session_id and new uuid
        audio_name = f'{turn.session_id}_{uuid4().hex}{ext}'

        gcs = GCSManager('audio')

        try:
            gcs.upload_from_fileobj(
                file_obj=audio_file.file,
                blob_name=audio_name,
                content_type=content_type,
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f'Failed to upload audio file: {str(e)}'
            ) from e

        # Create a new SessionTurn instance
        turn_data = turn.model_dump()
        turn_data['audio_uri'] = audio_name
        new_turn = SessionTurn(**turn_data)

        self.db.add(new_turn)
        self.db.commit()
        self.db.refresh(new_turn)

        return SessionTurnRead(
            id=new_turn.id,
            session_id=new_turn.session_id,
            speaker=new_turn.speaker,
            start_offset_ms=new_turn.start_offset_ms,
            end_offset_ms=new_turn.end_offset_ms,
            text=new_turn.text,
            audio_uri=audio_name,
            ai_emotion=new_turn.ai_emotion,
            created_at=new_turn.created_at,
        )
