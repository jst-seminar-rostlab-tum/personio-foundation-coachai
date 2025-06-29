import os
from pathlib import Path

from fastapi import HTTPException, UploadFile
from sqlmodel import Session as DBSession

from app.models.session import Session as SessionModel
from app.models.session_turn import SessionTurn
from app.schemas.session_turn import SessionTurnCreate, SessionTurnRead
from app.services.google_cloud_storage_service import GCSManager

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))  # app/services/
BASE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, '../../'))  # backend/
RECORDING_DIR = os.path.join(BASE_DIR, 'tmp', 'recordings')


class SessionTurnService:
    def __init__(self, db: DBSession) -> None:
        self.db = db

    def create_session_turn(
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

        audio_name = turn.audio_name
        if not audio_name:
            raise HTTPException(status_code=400, detail='Audio name is required')
        if not (audio_name.endswith('.mp3') or audio_name.endswith('.wav')):
            raise HTTPException(status_code=400, detail='Audio name must end with .mp3 or .wav')
        if not turn.text:
            raise HTTPException(status_code=400, detail='Text is required')

        # Create tmp folder if needed
        os.makedirs(RECORDING_DIR, exist_ok=True)

        # Check if the audio file is valid
        ext = os.path.splitext(audio_file.filename)[-1].lower()
        if ext not in ['.mp3', '.wav']:
            raise HTTPException(status_code=400, detail='Only .mp3 or .wav files are allowed')

        local_path = os.path.join(RECORDING_DIR, audio_name)

        with open(local_path, 'wb') as f:
            f.write(audio_file.file.read())

        gcs = GCSManager('audio')

        local_path = Path(local_path)

        # try:
        gcs.upload_single_document(file_path=local_path)
        # except Exception as e:
        #     raise HTTPException(status_code=500, detail=f"Failed to upload audio file: {str(e)}")

        # Create a new SessionTurn instance
        turn_data = turn.model_dump()
        turn_data['audio_uri'] = local_path.name
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
            audio_uri=local_path.name,
            ai_emotion=new_turn.ai_emotion,
            created_at=new_turn.created_at,
        )
