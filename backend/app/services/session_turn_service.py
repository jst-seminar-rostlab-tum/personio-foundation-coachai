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

# Stitching modes
MODE_CONCAT = 'concat'
MODE_TIMELINE = 'timeline'

# Set desired stitching mode for all stitching operations
STITCH_MODE = MODE_TIMELINE  # or MODE_TIMELINE


def convert_audio_to_mp3(upload_file: UploadFile) -> tuple[str, bytes]:
    """
    Converts an uploaded audio file to MP3 format and returns the filename and bytes.
    """
    input_ext = upload_file.filename.split('.')[-1].lower()
    with NamedTemporaryFile(delete=True, suffix=f'.{input_ext}') as temp_in:
        temp_in.write(upload_file.file.read())
        temp_in.flush()

        with NamedTemporaryFile(delete=True, suffix='.mp3') as temp_out:
            (
                ffmpeg.input(temp_in.name)
                .output(temp_out.name, format='mp3', audio_bitrate='64k')
                .overwrite_output()
                .run(quiet=True)
            )
            temp_out.seek(0)
            return temp_out.name, temp_out.read()


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
        self, turn: SessionTurnCreate, audio_file: UploadFile
    ) -> SessionTurnRead:
        session = self.db.get(SessionModel, turn.session_id)
        if not session:
            raise HTTPException(status_code=404, detail='Session not found')
        if not turn.text:
            raise HTTPException(status_code=400, detail='Text is required')

        audio_name = f'{turn.session_id}_{uuid4().hex}.mp3'
        gcs = GCSManager('audio')
        try:
            _, mp3_bytes = convert_audio_to_mp3(audio_file)
            gcs.upload_from_fileobj(BytesIO(mp3_bytes), audio_name, content_type='audio/mpeg')
        except Exception as e:
            raise HTTPException(status_code=500, detail=f'Failed to upload audio file: {e}') from e

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
            full_audio_start_offset_ms=new_turn.full_audio_start_offset_ms,
            text=new_turn.text,
            ai_emotion=new_turn.ai_emotion,
            created_at=new_turn.created_at,
        )

    def get_mp3_duration_bytesio(self, mp3_buffer: io.BytesIO) -> float:
        with tempfile.NamedTemporaryFile(suffix='.mp3') as tmp:
            tmp.write(mp3_buffer.getvalue())
            tmp.flush()
            cmd = [
                'ffprobe',
                '-v',
                'error',
                '-show_entries',
                'format=duration',
                '-of',
                'default=noprint_wrappers=1:nokey=1',
                tmp.name,
            ]
            res = subprocess.run(cmd, capture_output=True, text=True)
            return float(res.stdout.strip())

    def stitch_mp3s_from_gcs(self, session_id: UUID, output_blob_name: str) -> str | None:
        gcs = GCSManager('audio')
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
            gcs.bucket.blob(f'{gcs.prefix}{turn.audio_uri}').download_to_file(buf)
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
            gcs.upload_from_fileobj(out_buf, output_blob_name, content_type='audio/mpeg')
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
                session_id=t.session_id,
                speaker=t.speaker,
                full_audio_start_offset_ms=t.full_audio_start_offset_ms,
                text=t.text,
                ai_emotion=t.ai_emotion,
                created_at=t.created_at,
            )
            for t in turns
        ]
