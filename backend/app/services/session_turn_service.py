import io
import os
import subprocess
import tempfile
from uuid import UUID, uuid4

import puremagic
from fastapi import HTTPException, UploadFile
from sqlmodel import Session as DBSession
from sqlmodel import col, select

from app.config import Settings
from app.connections.gcs_client import get_gcs_audio_manager
from app.models.session import Session as SessionModel
from app.models.session_turn import SessionTurn
from app.schemas.session_turn import SessionTurnCreate, SessionTurnRead
from app.services.google_cloud_storage_service import GCSManager

settings = Settings()

# Stitching modes
MODE_CONCAT = 'concat'
MODE_TIMELINE = 'timeline'

# Set desired stitching mode for all stitching operations
STITCH_MODE = MODE_TIMELINE  # or MODE_TIMELINE


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
    def __init__(self, db: DBSession, gcs_manager: GCSManager | None = None) -> None:
        self.db = db
        self.gcs_manager = gcs_manager or get_gcs_audio_manager()

    async def create_session_turn(
        self, turn: SessionTurnCreate, audio_file: UploadFile
    ) -> SessionTurnRead:
        session = self.db.get(SessionModel, turn.session_id)
        if not session:
            raise HTTPException(status_code=404, detail='Session not found')
        if not turn.text:
            raise HTTPException(status_code=400, detail='Text is required')

        audio_uri = ''
        if settings.ENABLE_AI:
            audio_uri = store_audio_file(turn.session_id, audio_file)

        turn_data = turn.model_dump()
        turn_data['audio_uri'] = audio_uri
        new_turn = SessionTurn(**turn_data)
        self.db.add(new_turn)
        self.db.commit()
        self.db.refresh(new_turn)

        return SessionTurnRead(
            id=new_turn.id,
            speaker=new_turn.speaker,
            full_audio_start_offset_ms=new_turn.full_audio_start_offset_ms,
            text=new_turn.text,
            ai_emotion=new_turn.ai_emotion,
            created_at=new_turn.created_at,
        )

    def get_mp3_duration_bytesio(self, mp3_buffer: io.BytesIO) -> float:
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
            tmp.write(mp3_buffer.getvalue())
            tmp.flush()
            tmp_path = tmp.name

        cmd = [
            'ffprobe',
            '-v',
            'error',
            '-show_entries',
            'format=duration',
            '-of',
            'default=noprint_wrappers=1:nokey=1',
            tmp_path,
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        output = res.stdout.strip()

        try:
            duration = float(output)
        except ValueError:
            print(f"Could not parse duration from ffprobe output: '{output}'")
            duration = 0.0

        os.remove(tmp_path)
        return duration

    def stitch_mp3s_from_gcs(self, session_id: UUID, output_blob_name: str) -> str | None:
        # Order by configured start_offset_ms to respect timeline
        session_turns = self.db.exec(
            select(SessionTurn)
            .where(SessionTurn.session_id == session_id)
            .order_by(col(SessionTurn.start_offset_ms))
        ).all()
        if not session_turns:
            return None

        # Download, compute durations, and determine offsets
        mp3_entries = []  # list of (buffer, duration, offset_ms)
        cumulative = 0.0
        for turn in session_turns:
            buf = io.BytesIO()
            self.gcs_manager.bucket.blob(
                f'{self.gcs_manager.prefix}{turn.audio_uri}'
            ).download_to_file(buf)
            buf.seek(0)
            dur = self.get_mp3_duration_bytesio(buf)

            if STITCH_MODE == MODE_TIMELINE:
                offset = turn.start_offset_ms or 0
            else:
                offset = int(cumulative * 1000)
                cumulative += dur

            # Update the stored offset
            turn.full_audio_start_offset_ms = offset
            self.db.add(turn)
            mp3_entries.append((buf, dur, offset))

        self.db.commit()

        with tempfile.TemporaryDirectory() as tmpdir:
            inputs = []
            for idx, (buf, _, _) in enumerate(mp3_entries):
                path = os.path.join(tmpdir, f'{idx}.mp3')
                with open(path, 'wb') as f:
                    f.write(buf.getvalue())
                inputs.append(path)
                buf.close()

            if STITCH_MODE == MODE_CONCAT:
                list_txt = os.path.join(tmpdir, 'list.txt')
                with open(list_txt, 'w') as f:
                    for p in inputs:
                        f.write(f"file '{p}'\n")
                cmd = [
                    'ffmpeg',
                    '-hide_banner',
                    '-loglevel',
                    'error',
                    '-f',
                    'concat',
                    '-safe',
                    '0',
                    '-i',
                    list_txt,
                    '-c:a',
                    'libmp3lame',
                    '-q:a',
                    '2',
                    '-f',
                    'mp3',
                    'pipe:1',
                ]
            else:
                cmd = ['ffmpeg', '-hide_banner', '-loglevel', 'error']
                for p in inputs:
                    cmd += ['-i', p]
                # build delay filters
                delays, labels = [], []
                for i, (_, _, off) in enumerate(mp3_entries):
                    delays.append(f'[{i}:a]adelay={off}|{off}[d{i}]')
                    labels.append(f'[d{i}]')
                mix = ''.join(labels) + f'amix=inputs={len(mp3_entries)}:duration=longest[mixout]'
                filter_complex = ';'.join(delays + [mix])
                cmd += [
                    '-filter_complex',
                    filter_complex,
                    '-map',
                    '[mixout]',
                    '-c:a',
                    'libmp3lame',
                    '-q:a',
                    '2',
                    '-f',
                    'mp3',
                    'pipe:1',
                ]

            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            if proc.returncode != 0:
                raise RuntimeError(f'ffmpeg error: {err.decode()}')

            out_buf = io.BytesIO(out)
            out_buf.seek(0)
            self.gcs_manager.upload_from_fileobj(
                out_buf, output_blob_name, content_type='audio/mpeg'
            )
            out_buf.close()

        return output_blob_name

    def get_session_turns(self, session_id: UUID) -> list[SessionTurnRead]:
        turns = self.db.exec(
            select(SessionTurn)
            .where(SessionTurn.session_id == session_id)
            .order_by(col(SessionTurn.full_audio_start_offset_ms))
        ).all()
        return [
            SessionTurnRead(
                id=t.id,
                speaker=t.speaker,
                full_audio_start_offset_ms=t.full_audio_start_offset_ms,
                text=t.text,
                ai_emotion=t.ai_emotion,
                created_at=t.created_at,
            )
            for t in turns
        ]
