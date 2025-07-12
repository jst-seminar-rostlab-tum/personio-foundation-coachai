import logging
from datetime import UTC, datetime, timedelta

from sqlmodel import Session as DBSession
from sqlmodel import select

from app.connections.gcs_client import get_gcs_audio_manager
from app.models.session_feedback import SessionFeedback
from app.models.session_turn import SessionTurn


def cleanup_old_session_turns(db: DBSession) -> None:
    """
    Clean up old session_turn records and related GCS files.
    Delete session_turn records older than 90 days.
    Delete GCS files associated with the session_turn records.
    Clear the full_audio_filename field in session_feedback records.
    Commit the changes to the database.
    """
    threshold = datetime.now(UTC) - timedelta(days=90)
    turns = db.exec(select(SessionTurn).where(SessionTurn.created_at <= threshold)).all()
    if not turns:
        return
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
