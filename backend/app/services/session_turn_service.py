import io
import os
import subprocess
import tempfile
from io import BytesIO
from tempfile import NamedTemporaryFile
from uuid import UUID, uuid4

import ffmpeg
import puremagic
from fastapi import HTTPException, UploadFile
from sqlmodel import Session as DBSession
from sqlmodel import col, select

from app.models.session import Session as SessionModel
from app.models.session_turn import SessionTurn
from app.schemas.session_turn import SessionTurnCreate, SessionTurnRead
from app.services.google_cloud_storage_service import GCSManager


def convert_audio_to_mp3(upload_file: UploadFile) -> tuple[str, bytes]:
    """
    Converts an uploaded audio file to MP3 format and returns the filename and bytes.
    """
    input_ext = upload_file.filename.split('.')[-1].lower()
    with NamedTemporaryFile(delete=True, suffix=f'.{input_ext}') as temp_in:
        temp_in.write(upload_file.file.read())
        temp_in.flush()

        with NamedTemporaryFile(delete=True, suffix='.mp3') as temp_out:
            # Run ffmpeg to convert input to MP3
            (
                ffmpeg.input(temp_in.name)
                .output(
                    temp_out.name, format='mp3', audio_bitrate='64k'
                )  # adjust bitrate as needed
                .overwrite_output()
                .run(quiet=True)
            )
            temp_out.seek(0)
            converted_bytes = temp_out.read()
            return temp_out.name, converted_bytes


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

        # Generate a unique audio name using session_id and new uuid
        audio_name = f'{turn.session_id}_{uuid4().hex}.mp3'

        gcs = GCSManager('audio')

        try:
            # CONVERT to mp3 before uploading
            filename, mp3_bytes = convert_audio_to_mp3(audio_file)

            gcs.upload_from_fileobj(
                file_obj=BytesIO(mp3_bytes),
                blob_name=audio_name,
                content_type='audio/mpeg',
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

    def get_mp3_duration_bytesio(self, mp3_buffer: io.BytesIO) -> float:
        with tempfile.NamedTemporaryFile(suffix='.mp3') as tmpfile:
            tmpfile.write(mp3_buffer.getvalue())
            tmpfile.flush()
            ffprobe_cmd = [
                'ffprobe',
                '-v',
                'error',
                '-show_entries',
                'format=duration',
                '-of',
                'default=noprint_wrappers=1:nokey=1',
                tmpfile.name,
            ]
            result = subprocess.run(
                ffprobe_cmd,
                capture_output=True,
                text=True,
            )
            return float(result.stdout.strip())

    async def stitch_mp3s_from_gcs(
        self,
        session_id: UUID,
        output_blob_name: str,
    ) -> tuple[str | None, list[float]]:
        """
        Downloads a list of audio files from GCS, stitches them in order, and uploads
        the result to GCS.
        All temp files are cleaned up, and memory is flushed after upload.
        """

        gcs = GCSManager('audio')

        session_turns = self.db.exec(
            select(SessionTurn)
            .where(SessionTurn.session_id == session_id)
            .order_by(col(SessionTurn.start_offset_ms))
        ).all()

        print(session_turns)

        if not session_turns:
            return None, []

        # 1. Download to memory and calculate durations
        mp3_buffers = []
        turn_timestamps = []
        current_offset = 0.0

        for session_turn in session_turns:
            blob = gcs.bucket.blob(f'{gcs.prefix}{session_turn.audio_uri}')
            buf = io.BytesIO()
            blob.download_to_file(buf)
            buf.seek(0)
            mp3_buffers.append(buf)
            turn_timestamps.append(current_offset)
            duration = self.get_mp3_duration_bytesio(buf)
            session_turn.full_audio_start_offset_ms = int(current_offset * 1000)
            self.db.add(session_turn)
            current_offset += duration

        self.db.commit()

        # 2. Write to temp files for ffmpeg concat
        with tempfile.TemporaryDirectory() as tmpdir:
            input_files = []
            for i, buf in enumerate(mp3_buffers):
                input_path = os.path.join(tmpdir, f'{i}.mp3')
                with open(input_path, 'wb') as f:
                    f.write(buf.getvalue())
                input_files.append(input_path)
                buf.close()
            concat_file = os.path.join(tmpdir, 'inputs.txt')
            with open(concat_file, 'w') as f:
                for input_path in input_files:
                    f.write(f"file '{input_path}'\n")

            # Re-encode!
            ffmpeg_cmd = [
                'ffmpeg',
                '-hide_banner',
                '-loglevel',
                'error',
                '-f',
                'concat',
                '-safe',
                '0',
                '-i',
                concat_file,
                '-c:a',
                'libmp3lame',
                '-q:a',
                '2',
                '-f',
                'mp3',
                'pipe:1',
            ]
            proc = subprocess.Popen(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            output, err = proc.communicate()
            if proc.returncode != 0:
                raise RuntimeError(f'ffmpeg error: {err.decode()}')

            output_buffer = io.BytesIO(output)
            output_buffer.seek(0)
            gcs.upload_from_fileobj(
                file_obj=output_buffer, blob_name=output_blob_name, content_type='audio/mpeg'
            )
            output_buffer.close()

        return output_blob_name, turn_timestamps
