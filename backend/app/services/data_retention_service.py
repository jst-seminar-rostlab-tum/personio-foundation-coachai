import logging
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlmodel import Session as DBSession
from sqlmodel import select

from app.connections.gcs_client import get_gcs_audio_manager
from app.models.session_feedback import SessionFeedback
from app.models.session_turn import SessionTurn


def cleanup_old_session_turns(db: DBSession) -> None:
    """
    Clean up old session_turn records and related GCS files.
    Delete session_turn records older than 90 days.
    """
    threshold = datetime.now(UTC) - timedelta(days=90)
    turns = db.exec(select(SessionTurn).where(SessionTurn.created_at <= threshold)).all()
    if not turns:
        return
    delete_session_turns_and_audio_files(db, turns)
    logging.info(f'Deleted {len(turns)} old session_turn records older than 90 days.')


def delete_session_turns_and_audio_files(db: DBSession, turns: Sequence[SessionTurn]) -> None:
    """
    Delete session_turn records and associated GCS audio files.
    For each turn:
    1. Delete the GCS file referenced by audio_uri.
    2. Check if session_feedback references this audio_uri and delete the GCS file if
         it exists, then clear the full_audio_filename field.
    3. Delete the session_turn record.
    """

    gcs = get_gcs_audio_manager()
    for turn in turns:
        audio_uri = turn.audio_uri
        # 1. Delete GCS file (audio_uri)
        if gcs and audio_uri:
            try:
                gcs.delete_document(audio_uri)
            except Exception as e:
                logging.warning(f'Failed to delete GCS audio file {audio_uri}: {e}')
        # 2. Check if session_feedback references this audio_uri
        feedbacks = db.exec(
            select(SessionFeedback).where(SessionFeedback.full_audio_filename == audio_uri)
        ).all()
        for feedback in feedbacks:
            # Delete GCS file (if not deleted above, GCSManager internally checks for existence)
            if gcs and feedback.full_audio_filename:
                try:
                    gcs.delete_document(feedback.full_audio_filename)
                except Exception as e:
                    logging.warning(
                        f'Failed to delete GCS feedback audio {feedback.full_audio_filename}: {e}'
                    )
            # Clear full_audio_filename field
            feedback.full_audio_filename = ''
            db.add(feedback)
        # 3. Delete session_turn record
        try:
            db.delete(turn)
        except Exception as e:
            logging.warning(f'Failed to delete session_turn {turn.id}: {e}')
    db.commit()


def delete_session_turns_by_session_id(db: DBSession, session_id: UUID) -> None:
    """
    Delete all session_turn records for a given session_id.
    """
    turns = db.exec(select(SessionTurn).where(SessionTurn.session_id == session_id)).all()
    if not turns:
        return
    delete_session_turns_and_audio_files(db, turns)
    logging.info(f'Deleted {len(turns)} session_turn records for session {session_id}.')


def delete_full_audio_for_feedback_by_session_id(db: DBSession, session_id: UUID) -> None:
    """
    Delete all full audio files from GCS referenced by SessionFeedback.full_audio_filename
    for a given session_id, and set full_audio_filename to an empty string.
    """
    gcs = get_gcs_audio_manager()
    feedbacks = db.exec(
        select(SessionFeedback).where(SessionFeedback.session_id == session_id)
    ).all()
    for feedback in feedbacks:
        audio_uri = feedback.full_audio_filename
        if gcs and audio_uri:
            try:
                if gcs.document_exists(audio_uri):
                    gcs.delete_document(audio_uri)
            except Exception as e:
                logging.warning(f'Failed to delete GCS feedback audio {audio_uri}: {e}')
        feedback.full_audio_filename = ''
        db.add(feedback)
    db.commit()
