import io
import os
import re
import subprocess
import tempfile
from uuid import uuid4

import puremagic
from fastapi import BackgroundTasks, HTTPException, UploadFile, status
from sqlalchemy import UUID
from sqlmodel import Session as DBSession
from sqlmodel import col, select

from app.config import Settings
from app.connections.gcs_client import get_gcs_audio_manager
from app.enums.speaker import SpeakerType
from app.models.session import Session as SessionModel
from app.models.session_turn import SessionTurn
from app.models.user_profile import UserProfile
from app.schemas.session_turn import (
    SessionTurnCreate,
    SessionTurnRead,
    SessionTurnStitchAudioSuccess,
)
from app.services.live_feedback_service import generate_and_store_live_feedback
from app.services.vector_db_context_service import get_hr_docs_context

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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Only .webm, .mp3 or .wav files are allowed',
        )
    mime = matches[0].mime_type
    if not is_valid_audio_mime_type(mime):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Only .webm, .mp3 or .wav files are allowed',
        )
    return mime


def get_file_extension_from_content_type(content_type: str) -> str:
    mapping = {
        'audio/webm': '.webm',
        'video/webm': '.webm',
        'audio/mpeg': '.mp3',
        'video/mpeg': '.mp3',
        'audio/wav': '.wav',
        'audio/x-wav': '.wav',
        'audio/wave': '.wav',
    }
    ext = mapping.get(content_type)
    if not ext:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Only .webm, .mp3 or .wav files are allowed',
        )
    return ext


def store_audio_file(session_id: UUID, audio_file: UploadFile) -> str:
    content_type = get_audio_content_type(audio_file)
    file_extension = get_file_extension_from_content_type(content_type)
    audio_name = f'{session_id}_{uuid4().hex}{file_extension}'
    gcs = get_gcs_audio_manager()

    try:
        gcs.upload_from_fileobj(
            file_obj=audio_file.file,
            blob_name=audio_name,
            content_type=get_audio_content_type(audio_file),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Failed to upload audio file'
        ) from e

    return audio_name


class SessionTurnService:
    def __init__(self, db: DBSession) -> None:
        self.db = db
        self.gcs_manager = get_gcs_audio_manager()

    async def create_session_turn(
        self,
        turn: SessionTurnCreate,
        audio_file: UploadFile,
        user_profile: UserProfile,
        background_tasks: BackgroundTasks,
    ) -> SessionTurnRead:
        session = self.db.get(SessionModel, turn.session_id)

        if not session.scenario.user_id == user_profile.id:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, detail='User does not own this session'
            )
        if not session:
            raise HTTPException(status_code=404, detail='Session not found')
        if not turn.text:
            raise HTTPException(status_code=400, detail='Text is required')

        audio_uri = ''
        if self.gcs_manager is not None:
            audio_uri = store_audio_file(turn.session_id, audio_file)

        turn_data = turn.model_dump()
        turn_data['audio_uri'] = audio_uri
        new_turn = SessionTurn(**turn_data)
        self.db.add(new_turn)
        self.db.commit()
        self.db.refresh(new_turn)

        if turn.speaker == SpeakerType.user:
            category = session.scenario.category.name if session.scenario.category else ''
            hr_docs_context, _ = get_hr_docs_context(
                persona=session.scenario.persona,
                situational_facts=session.scenario.situational_facts,
                category=category,
            )

            # Generate live feedback item in the background
            background_tasks.add_task(
                generate_and_store_live_feedback,
                db_session=self.db,
                session_id=turn.session_id,
                session_turn_context=new_turn,
                hr_docs_context=hr_docs_context,
            )

        return SessionTurnRead(
            id=new_turn.id,
            speaker=new_turn.speaker,
            full_audio_start_offset_ms=new_turn.full_audio_start_offset_ms,
            text=new_turn.text,
            ai_emotion=new_turn.ai_emotion,
            created_at=new_turn.created_at,
        )

    def get_audio_duration_seconds(self, buffer: io.BytesIO) -> float:
        """
        Write buffer to a temp file and return its audio duration in seconds.
        Four fallbacks, in order:
        1) ffprobe container duration
        2) ffprobe audio‐stream duration
        3) parse “Duration: hh:mm:ss.xx” from ffmpeg -i stderr
        4) decode with ffmpeg -f null and grab the last time= log
        """
        # 1) dump to temp file
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(buffer.getvalue())
            tmp.flush()
            path = tmp.name

        # --- 1) container duration ---
        res = subprocess.run(
            [
                'ffprobe',
                '-v',
                'error',
                '-show_entries',
                'format=duration',
                '-of',
                'default=noprint_wrappers=1:nokey=1',
                path,
            ],
            capture_output=True,
            text=True,
        )
        dur = res.stdout.strip()
        try:
            return float(dur)
        except ValueError:
            pass

        # --- 2) audio‐stream duration ---
        res2 = subprocess.run(
            [
                'ffprobe',
                '-v',
                'error',
                '-select_streams',
                'a:0',
                '-show_entries',
                'stream=duration',
                '-of',
                'default=noprint_wrappers=1:nokey=1',
                path,
            ],
            capture_output=True,
            text=True,
        )
        dur2 = res2.stdout.strip()
        try:
            return float(dur2)
        except ValueError:
            pass

        # --- 3) parse “Duration: hh:mm:ss.xx” from `ffmpeg -i` banner ---
        res3 = subprocess.run(['ffmpeg', '-i', path], capture_output=True, text=True)
        info = res3.stderr + res3.stdout
        m = re.search(r'Duration:\s*(\d+):(\d+):(\d+\.\d+)', info)
        if m:
            hh, mm, ss = m.groups()
            return int(hh) * 3600 + int(mm) * 60 + float(ss)

        # --- 4) brute‐force decode & scrape final “time=…” log ---
        res4 = subprocess.run(
            [
                'ffmpeg',
                '-i',
                path,
                '-vn',
                '-sn',
                '-dn',  # skip video, subtitles, data
                '-f',
                'null',
                '-',
            ],  # output to “nowhere”
            capture_output=True,
            text=True,
        )
        # find all occurrences like “time=00:01:23.45”
        times = re.findall(r'time=(\d+:\d+:\d+\.\d+)', res4.stderr)
        if times:
            last = times[-1]
            hh, mm, ss = last.split(':')
            return int(hh) * 3600 + int(mm) * 60 + float(ss)

        # if we still failed:
        raise RuntimeError(f'Could not determine duration (ffprobe fmt={dur!r}, stream={dur2!r})')

    def stitch_mp3s_from_gcs(
        self, session_id: UUID, output_blob_name: str
    ) -> SessionTurnStitchAudioSuccess | None:
        # Order by configured start_offset_ms to respect timeline

        if not settings.ENABLE_AI:
            return None

        if self.gcs_manager is None:
            raise HTTPException(status_code=500, detail='Failed to connect to audio storage')

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
        longest_end_ms = 0
        for turn in session_turns:
            buf = io.BytesIO()
            self.gcs_manager.bucket.blob(
                f'{self.gcs_manager.prefix}{turn.audio_uri}'
            ).download_to_file(buf)
            buf.seek(0)
            dur = self.get_audio_duration_seconds(buf)  # seconds (float)

            # decide the clip’s offset
            if STITCH_MODE == MODE_TIMELINE:
                offset_ms = turn.start_offset_ms or 0
            else:  # MODE_CONCAT
                offset_ms = int(cumulative * 1000)
                cumulative += dur

            # remember the clip’s absolute end position
            end_ms = offset_ms + int(dur * 1000)
            longest_end_ms = max(longest_end_ms, end_ms)

            # store/update DB as before
            turn.full_audio_start_offset_ms = offset_ms
            self.db.add(turn)
            mp3_entries.append((buf, dur, offset_ms))

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

        print(f'Stitched audio saved to {output_blob_name}')
        stitched_duration_s = longest_end_ms / 1000.0  # convert back to seconds
        print(f'Stitched audio duration: {stitched_duration_s} seconds')

        return SessionTurnStitchAudioSuccess(
            output_filename=output_blob_name, audio_duration_s=int(stitched_duration_s)
        )

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

    def delete_session_turns(self, session_turns: list[SessionTurn]) -> list[str]:
        if not session_turns:
            return []

        deleted_audios = []

        for turn in session_turns:
            if turn.audio_uri and self.gcs_manager:
                try:
                    self.gcs_manager.delete_document(turn.audio_uri)
                    deleted_audios.append(turn.audio_uri)
                except Exception as e:
                    raise HTTPException(
                        status_code=500, detail=f'Failed to delete audio file: {e}'
                    ) from e

            self.db.delete(turn)
        self.db.commit()

        return deleted_audios
