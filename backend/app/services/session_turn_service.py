"""Service layer for session turn service."""

import io
import logging
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
from app.dependencies.database import get_db_session
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
    """Check whether a MIME type is supported for audio uploads.

    Parameters:
        mime_type (str): MIME type to validate.

    Returns:
        bool: True if the MIME type is supported.
    """
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
    """Detect and validate the MIME type of an uploaded audio file.

    Parameters:
        upload_file (UploadFile): Uploaded file object.

    Returns:
        str: Detected MIME type.

    Raises:
        HTTPException: If the file type is not supported.
    """
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
    """Map a MIME type to a file extension.

    Parameters:
        content_type (str): MIME type to map.

    Returns:
        str: File extension for the MIME type.

    Raises:
        HTTPException: If the content type is unsupported.
    """
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
    """Upload an audio file to GCS and return its blob name.

    Parameters:
        session_id (UUID): Session identifier for naming.
        audio_file (UploadFile): Uploaded audio file.

    Returns:
        str: Stored audio blob name.

    Raises:
        HTTPException: If the upload fails.
    """
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
    """Service for managing session turns and audio stitching."""

    def __init__(self, db: DBSession) -> None:
        """Initialize the service with a database session.

        Parameters:
            db (DBSession): Database session used for queries and updates.
        """
        self.db = db
        self.gcs_manager = get_gcs_audio_manager()

    async def create_session_turn(
        self,
        turn: SessionTurnCreate,
        audio_file: UploadFile,
        user_profile: UserProfile,
        background_tasks: BackgroundTasks,
    ) -> SessionTurnRead:
        """Create a session turn and optionally generate live feedback.

        Parameters:
            turn (SessionTurnCreate): Turn payload.
            audio_file (UploadFile): Uploaded audio file.
            user_profile (UserProfile): Requesting user profile.
            background_tasks (BackgroundTasks): Background task manager.

        Returns:
            SessionTurnRead: Created turn payload.

        Raises:
            HTTPException: If session validation fails.
        """
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
            hr_docs_context, _, _ = get_hr_docs_context(
                persona=session.scenario.persona,
                situational_facts=session.scenario.situational_facts,
                category=category,
            )

            language = session.scenario.language_code if session.scenario else 'en'
            # Generate live feedback item in the background
            background_tasks.add_task(
                generate_and_store_live_feedback,
                session_id=turn.session_id,
                session_turn_context=new_turn,
                hr_docs_context=hr_docs_context,
                session_generator_func=get_db_session,
                language=language,
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
        """Write buffer to a temp file and return its audio duration in seconds.
        Four fallbacks, in order:
        1) ffprobe container duration
        2) ffprobe audio‐stream duration
        3) parse “Duration: hh:mm:ss.xx” from ffmpeg -i stderr
        4) decode with ffmpeg -f null and grab the last time= log

        Parameters:
            buffer (io.BytesIO): Audio buffer to analyze.

        Returns:
            float: Audio duration in seconds.

        Raises:
            RuntimeError: If duration cannot be determined.
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
        """Stitch session turn audio files into a single MP3.

        Parameters:
            session_id (UUID): Session identifier.
            output_blob_name (str): Destination blob name for stitched audio.

        Returns:
            SessionTurnStitchAudioSuccess | None: Stitching result or None when skipped.

        Raises:
            HTTPException: If storage access is unavailable.
            RuntimeError: If ffmpeg processing fails.
        """
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
                total_s = longest_end_ms / 1000.0

                for p in inputs:
                    cmd += ['-i', p]

                filters = []

                # 0) a silent guide track that defines the final length
                filters.append(f'aevalsrc=0:d={total_s}[base]')

                # 1) one chain per real clip, all resampled to 48 kHz and
                #    delayed on *every* channel
                for i, (_, _, off) in enumerate(mp3_entries):
                    filters.append(f'[{i}:a]aresample=48000,adelay={off}|{off}:all=1[d{i}]')

                mix_inputs = '[base]' + ''.join(f'[d{i}]' for i in range(len(mp3_entries)))
                filters.append(
                    f'{mix_inputs}'
                    f'amix=inputs={len(mp3_entries) + 1}:duration=first:normalize=0[mix]'
                )

                cmd += [
                    '-filter_complex',
                    ';'.join(filters),
                    '-map',
                    '[mix]',
                    '-c:a',
                    'libmp3lame',
                    '-b:a',
                    '192k',  # use CBR so duration is correct
                    '-compression_level',
                    '0',
                    '-write_xing',
                    '0',  # no VBR header on a pipe
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

            # proc = subprocess.run(cmd, stdout=subprocess.PIPE, check=True)
            # data = proc.stdout  # bytes
            self.gcs_manager.delete_document(output_blob_name)
            self.gcs_manager.upload_from_fileobj(
                out_buf, output_blob_name, content_type='audio/mpeg'
            )

            out_buf.close()

        logging.info(f'Stitched audio saved to {output_blob_name}')
        stitched_duration_s = longest_end_ms / 1000.0  # convert back to seconds

        return SessionTurnStitchAudioSuccess(
            output_filename=output_blob_name, audio_duration_s=int(stitched_duration_s)
        )

    def get_session_turns(self, session_id: UUID) -> list[SessionTurnRead]:
        """Fetch session turns ordered by stitched audio offsets.

        Parameters:
            session_id (UUID): Session identifier.

        Returns:
            list[SessionTurnRead]: Session turn summaries.
        """
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
        """Delete session turns and associated audio files.

        Parameters:
            session_turns (list[SessionTurn]): Turns to delete.

        Returns:
            list[str]: Deleted audio blob names.

        Raises:
            HTTPException: If audio deletion fails.
        """
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
