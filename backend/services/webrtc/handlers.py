import logging

from fastapi import WebSocket

from ...schemas.webrtc_schema import (
    TranscriptMessage,
    WebRTCMessage,
    WebRTCSignalingType,
    WebRTCTranscript,
)
from .webrtc_base import message_factory, signal_handler

logger = logging.getLogger(__name__)


@message_factory(WebRTCSignalingType.TRANSCRIPT)
async def create_transcript_message(data: WebRTCTranscript, websocket: WebSocket) -> WebRTCMessage:
    """Create a transcript message"""
    logger.info(f'Creating transcript message from data: {data}')

    transcript_info = data.get('transcript', {})
    return WebRTCTranscript(
        type=WebRTCSignalingType.TRANSCRIPT,
        transcript=TranscriptMessage(
            text=transcript_info.get('text', ''),
            timestamp=transcript_info.get('timestamp', ''),
            confidence=transcript_info.get('confidence'),
            language=transcript_info.get('language'),
        ),
    )


@signal_handler(WebRTCSignalingType.TRANSCRIPT)
async def handle_transcript(message: WebRTCTranscript, peer_id: str) -> None:
    """Handle transcript messages with detailed logging"""
    logger.info(
        f'Received transcript from peer {peer_id}:\n'
        f'  Text: {message.transcript.text}\n'
        f'  Timestamp: {message.transcript.timestamp}\n'
        f'  Confidence: {message.transcript.confidence}\n'
        f'  Language: {message.transcript.language}'
    )
