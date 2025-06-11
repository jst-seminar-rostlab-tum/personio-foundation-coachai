from __future__ import annotations

import asyncio
import json
import logging
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Union

from aiortc import (
    RTCConfiguration,
    RTCDataChannel,
    RTCIceServer,
    RTCPeerConnection,
    RTCRtpTransceiver,
)
from aiortc.mediastreams import MediaStreamTrack
from google.genai import types

from app.schemas.webrtc_schema import (
    WebRTCDataChannelError,
    WebRTCMediaError,
    WebRTCPeerError,
)
from app.services.audio_processor import (
    AudioStreamTrack,
)
from app.services.webrtc_audio_service import WebRTCAudioLoop, webrtc_audio_service
from app.services.webrtc_event_manager import (
    PeerEventManager,
    webrtc_event_manager,
)
from app.services.webrtc_events import (
    WebRTCAudioEvent,
    WebRTCAudioEventType,
    WebRTCDataChannelEvent,
    WebRTCDataChannelEventType,
    WebRTCSessionEvent,
    WebRTCSessionEventType,
    WebRTCUserEvent,
    WebRTCUserEventType,
)

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

RTC_CONFIG = RTCConfiguration(
    iceServers=[
        RTCIceServer(
            urls=[
                'stun:stun.l.google.com:19302',
            ]
        ),
    ]
)

# Callback type definitions
SendToGeminiType = Union[types.Blob, WebRTCAudioEvent, types.Content]
SendToGeminiCallback = Callable[[SendToGeminiType], Awaitable[None]]

# Note: WebRTCEventManager moved to app.services.webrtc_event_manager


@dataclass
class Peer:
    """Peer connection and its associated resources"""

    peer_id: str
    connection: RTCPeerConnection
    transceiver: RTCRtpTransceiver | None = None
    data_channel: RTCDataChannel | None = None
    audio_loop: WebRTCAudioLoop | None = None  # Forward reference

    async def cleanup(self) -> None:
        """Cleanup all resources associated with this peer"""
        # Clean up audio loop through audio service
        if self.audio_loop:
            await self.audio_loop.stop()
        # Clean up transceiver
        if self.transceiver:
            self.transceiver.stop()
        # Clean up data channel
        if self.data_channel:
            self.data_channel.close()
        # Close peer connection
        await self.connection.close()


class PeerSessionManager:
    """Manage the lifecycle of WebRTC Peer connections"""

    def __init__(self) -> None:
        self.peers: dict[str, Peer] = {}
        # Event-driven callbacks - will be set by WebRTCService
        self.on_track_callback: Callable[[MediaStreamTrack, str], Awaitable[None]] | None = None
        self.on_datachannel_callback: Callable[[RTCDataChannel, str], Awaitable[None]] | None = None

    def set_track_callback(
        self, callback: Callable[[MediaStreamTrack, str], Awaitable[None]]
    ) -> None:
        """Set callback for track events"""
        self.on_track_callback = callback

    def set_datachannel_callback(
        self, callback: Callable[[RTCDataChannel, str], Awaitable[None]]
    ) -> None:
        """Set callback for data channel events"""
        self.on_datachannel_callback = callback

    async def create_peer(self, peer_id: str) -> Peer:
        """Create a new Peer connection"""
        if peer_id in self.peers:
            logger.debug(f'Peer {peer_id} already exists, closing old connection')
            await self.peers[peer_id].cleanup()
            del self.peers[peer_id]

        # Create peer connection
        pc = RTCPeerConnection(RTC_CONFIG)

        # Add transceiver for audio
        try:
            transceiver = pc.addTransceiver('audio', direction='sendrecv')
            logger.debug(f'Created transceiver for peer {peer_id}')
        except Exception as e:
            raise WebRTCMediaError(f'Failed to create audio transceiver: {str(e)}', peer_id) from e

        @pc.on('datachannel')
        async def on_datachannel(channel: RTCDataChannel) -> None:
            logger.info(f'[PeerSessionManager] Data channel event triggered for peer {peer_id}')
            logger.info(f'[PeerSessionManager] Data channel label: {channel.label}')
            logger.info(f'[PeerSessionManager] Data channel state: {channel.readyState}')
            logger.info(f'[PeerSessionManager] Data channel protocol: {channel.protocol}')
            if self.on_datachannel_callback:
                await self.on_datachannel_callback(channel, peer_id)
            else:
                logger.warning(
                    f'[PeerSessionManager] No data channel callback set for peer {peer_id}'
                )

        @pc.on('track')
        async def on_track(track: MediaStreamTrack) -> None:
            if self.on_track_callback:
                await self.on_track_callback(track, peer_id)

        peer = Peer(connection=pc, peer_id=peer_id, transceiver=transceiver)
        self.peers[peer_id] = peer
        logger.info(f'Peer connection created for peer {peer_id}')
        return peer

    async def close_peer(self, peer_id: str) -> None:
        """Close a Peer connection"""
        try:
            if peer_id in self.peers:
                await self.peers[peer_id].cleanup()
                del self.peers[peer_id]
                logger.info(f'Peer connection closed for peer {peer_id}')
        except Exception as e:
            raise WebRTCPeerError(f'Error closing peer connection: {str(e)}', peer_id) from e

    def get_peer(self, peer_id: str) -> Peer | None:
        """Get the specified Peer"""
        return self.peers.get(peer_id)


class WebRTCService:
    """Business orchestration layer for WebRTC service"""

    def __init__(self) -> None:
        """Initialize the WebRTC service"""
        self.peer_session_manager = PeerSessionManager()

        # Set callbacks
        self.peer_session_manager.set_track_callback(self._handle_audio_track)
        self.peer_session_manager.set_datachannel_callback(self._handle_data_channel)

    def register_event_handlers(self, audio_loop: WebRTCAudioLoop) -> None:
        """Register event handlers using decorators for the audio loop"""
        event_manager = audio_loop.event_manager

        # Register transcript handler using event system instead of callback
        @event_manager.on_data_channel_event(WebRTCDataChannelEventType.TRANSCRIPT_SENT)
        async def on_transcript_sent(event: WebRTCDataChannelEvent) -> None:
            """Handle transcript sent event - replaces TranscriptCallback"""
            transcript = event.data.get('transcript', '') if event.data else ''
            peer_id = event.peer_id
            logger.info(f'[EventHandler] Transcript sent for peer {peer_id}: {transcript}')

            # Call the original transcript handler logic
            await self._handle_transcript(transcript, peer_id)

        # Register audio stream events
        @event_manager.on_audio_event(WebRTCAudioEventType.AUDIO_STREAM_START)
        async def on_audio_stream_start(event: WebRTCAudioEvent) -> None:
            """Handle audio stream start - replaces part of AudioTrackCallback"""
            peer_id = event.peer_id
            logger.info(f'[EventHandler] Audio stream started for peer {peer_id}')

        @event_manager.on_audio_event(WebRTCAudioEventType.VOICE_ACTIVITY_DETECTED)
        async def on_voice_activity(event: WebRTCAudioEvent) -> None:
            """Handle voice activity detection"""
            peer_id = event.peer_id
            audio_length = event.data.get('audio_length', 0) if event.data else 0
            logger.info(
                f'[EventHandler] Voice activity detected for peer {peer_id}, length: {audio_length}'
            )

        @event_manager.on_audio_event(WebRTCAudioEventType.SILENCE_DETECTED)
        async def on_silence_detected(event: WebRTCAudioEvent) -> None:
            """Handle silence detection"""
            peer_id = event.peer_id
            duration = event.data.get('duration', 0) if event.data else 0
            logger.info(
                f'[EventHandler] Silence detected for peer {peer_id}, duration: {duration:.2f}s'
            )

        # Register data channel events
        @event_manager.on_data_channel_event(WebRTCDataChannelEventType.CHANNEL_READY)
        async def on_channel_ready(event: WebRTCDataChannelEvent) -> None:
            """Handle data channel ready - replaces DataChannelCallback"""
            peer_id = event.peer_id
            logger.info(f'[EventHandler] Data channel ready for peer {peer_id}')

        @event_manager.on_data_channel_event(WebRTCDataChannelEventType.CHANNEL_CLOSED)
        async def on_channel_closed(event: WebRTCDataChannelEvent) -> None:
            """Handle data channel closed"""
            peer_id = event.peer_id
            logger.info(f'[EventHandler] Data channel closed for peer {peer_id}')

        # Register session events
        @event_manager.on_session_event(WebRTCSessionEventType.SESSION_STARTED)
        async def on_session_started(event: WebRTCSessionEvent) -> None:
            """Handle session started"""
            peer_id = event.peer_id
            logger.info(f'[EventHandler] WebRTC session started for peer {peer_id}')

        @event_manager.on_session_event(WebRTCSessionEventType.GEMINI_CONNECTED)
        async def on_gemini_connected(event: WebRTCSessionEvent) -> None:
            """Handle Gemini connection"""
            peer_id = event.peer_id
            logger.info(f'[EventHandler] Gemini connected for peer {peer_id}')

        @event_manager.on_session_event(WebRTCSessionEventType.GEMINI_DISCONNECTED)
        async def on_gemini_disconnected(event: WebRTCSessionEvent) -> None:
            """Handle Gemini disconnection"""
            peer_id = event.peer_id
            logger.info(f'[EventHandler] Gemini disconnected for peer {peer_id}')

        @event_manager.on_session_event(WebRTCSessionEventType.SESSION_ERROR)
        async def on_session_error(event: WebRTCSessionEvent) -> None:
            """Handle session error"""
            peer_id = event.peer_id
            error = event.data.get('error', 'Unknown error') if event.data else 'Unknown error'
            logger.error(f'[EventHandler] Session error for peer {peer_id}: {error}')

        # Register user events (for future text message handling)
        @event_manager.on_user_event(WebRTCUserEventType.USER_MESSAGE_SENT)
        async def on_user_message_sent(event: WebRTCUserEvent) -> None:
            """Handle user message sent - replaces SendToGeminiCallback for text"""
            peer_id = event.peer_id
            message = event.data.get('message', '') if event.data else ''
            logger.info(f'[EventHandler] User message sent for peer {peer_id}: {message}')

            # Send to Gemini if audio_loop is available
            if audio_loop and audio_loop.gemini_session:
                try:
                    content = types.Content(role='user', parts=[types.Part(text=message)])
                    await audio_loop.send_to_gemini(content)
                    logger.info(
                        f'[EventHandler] Successfully sent user message to Gemini: {message}'
                    )
                except Exception as e:
                    logger.error(f'[EventHandler] Failed to send user message to Gemini: {e}')

        logger.info(
            f'[WebRTCService] Registered event handlers for peer {audio_loop.peer_id}: '
            f'audio={len(event_manager.audio_event_handlers)}, '
            f'session={len(event_manager.session_event_handlers)}, '
            f'data_channel={len(event_manager.data_channel_event_handlers)}, '
            f'user={len(event_manager.user_event_handlers)}'
        )

    async def _handle_data_channel(self, channel: RTCDataChannel, peer_id: str) -> None:
        """Handle data channel events"""
        try:
            logger.info(f'[DataChannel] Received data channel: {channel.label}')

            if channel.label == 'transcript':
                peer = self.peer_session_manager.get_peer(peer_id)
                if peer:
                    peer.data_channel = channel
                    logger.info(f'[DataChannel] Assigned transcript channel to peer {peer_id}')

                    # If audio_loop already exists and channel is already open,
                    # mark as ready immediately
                    if peer.audio_loop and channel.readyState == 'open':
                        logger.info(
                            f'[DataChannel] Channel already open, '
                            f'marking audio_loop as ready for peer {peer_id}'
                        )
                        peer.audio_loop.mark_data_channel_ready()

                @channel.on('open')
                def on_transcript_open() -> None:
                    logger.info(f'[DataChannel] Transcript channel opened for peer {peer_id}')

                    # Notify WebRTCAudioLoop that data channel is ready
                    peer = self.peer_session_manager.get_peer(peer_id)
                    if peer and peer.audio_loop:
                        logger.info(
                            f'[DataChannel] Notifying audio_loop that channel is ready '
                            f'for peer {peer_id}'
                        )
                        peer.audio_loop.mark_data_channel_ready()
                    else:
                        logger.warning(
                            f'[DataChannel] No audio_loop found when channel opened '
                            f'for peer {peer_id}'
                        )

                    # Send a test message to verify the channel works
                    try:
                        test_message = json.dumps(
                            {'type': 'test', 'message': 'Data channel established'}
                        )
                        channel.send(test_message)
                        logger.info(f'[DataChannel] Test message sent to peer {peer_id}')
                    except Exception as test_error:
                        logger.error(
                            f'[DataChannel] Failed to send test message to peer {peer_id}: '
                            f'{test_error}'
                        )

                @channel.on('close')
                def on_transcript_close() -> None:
                    logger.info(f'[DataChannel] Transcript channel closed for peer {peer_id}')

                    # Emit channel closed event
                    peer = self.peer_session_manager.get_peer(peer_id)
                    if peer and peer.audio_loop:
                        asyncio.create_task(
                            peer.audio_loop.event_manager.emit_data_channel_event(
                                WebRTCDataChannelEventType.CHANNEL_CLOSED,
                                {'message': 'Data channel closed'},
                            )
                        )

                @channel.on('message')
                def on_transcript_message(message: str) -> None:
                    logger.info(
                        f'[DataChannel] Received transcript message from peer {peer_id}: {message}'
                    )

                @channel.on('error')
                def on_transcript_error(error: Exception) -> None:
                    logger.error(
                        f'[DataChannel] Transcript channel error for peer {peer_id}: {error}'
                    )
            else:
                logger.warning(
                    f'[DataChannel] Received unexpected data channel with label: {channel.label}'
                )

            logger.debug(f'[DataChannel] Stored received data channel for peer {peer_id}')
        except Exception as e:
            logger.error(
                f'[DataChannel] Error handling data channel for peer {peer_id}: {str(e)}',
                exc_info=True,
            )
            raise WebRTCDataChannelError(f'Error handling data channel: {str(e)}', peer_id) from e

    async def _handle_audio_track(self, track: MediaStreamTrack, peer_id: str) -> None:
        """Handle audio track events"""
        try:
            logger.info(f'Track {track.kind} received for peer {peer_id} at {time.time()}')
            if track.kind == 'audio':
                logger.info(
                    f'[WebRTC] Audio track received for peer {peer_id}, '
                    f'setting up WebRTC Audio Loop pipeline'
                )

            # Get peer object
            peer = self.peer_session_manager.get_peer(peer_id)
            if not peer:
                raise WebRTCPeerError(f'Peer {peer_id} not found', peer_id)

            logger.info(
                f'[WebRTC] Data channel exists: {peer.data_channel is not None} for peer {peer_id}'
            )
            if peer.data_channel:
                logger.info(
                    f'[WebRTC] Data channel state: {peer.data_channel.readyState} '
                    f'for peer {peer_id}'
                )

            # Create WebRTC Audio Loop
            audio_loop = webrtc_audio_service.create_audio_loop(peer_id)
            logger.info(f'[WebRTC] Audio loop created for peer {peer_id} at {time.time()}')

            # Create and set up the outbound audio track using our streamable version
            server_audio_track = AudioStreamTrack()
            if peer.transceiver and peer.transceiver.sender:
                peer.transceiver.sender.replaceTrack(server_audio_track)
            else:
                raise WebRTCMediaError(f'Cannot find sender for peer {peer_id}', peer_id)

            # Register to Peer object
            peer.audio_loop = audio_loop
            logger.info(f'[WebRTC] Audio loop assigned to peer {peer_id}')

            # Register event handlers (replaces old callback system)
            self.register_event_handlers(audio_loop)

            # Check if data channel is already open (timing issue fix)
            if peer.data_channel and peer.data_channel.readyState == 'open':
                logger.info(
                    f'[WebRTC] Data channel already open for peer {peer_id}, marking as ready'
                )
                audio_loop.mark_data_channel_ready()
            elif peer.data_channel:
                logger.info(
                    f'[WebRTC] Data channel exists but not open '
                    f'(state: {peer.data_channel.readyState}) for peer {peer_id}'
                )
                # Still mark as ready - the transcript handler will wait for the channel to open
                logger.info(f'[WebRTC] Marking audio_loop as ready anyway for peer {peer_id}')
                audio_loop.mark_data_channel_ready()
            else:
                logger.warning(f'[WebRTC] No data channel found for peer {peer_id}')

            # Start audio loop with the streamable track
            await audio_loop.start(track, peer, server_audio_track)
            logger.info(f'[WebRTC] WebRTCAudioLoop started for peer {peer_id}')

            logger.debug('WebRTC Audio Loop pipeline setup completed')

        except Exception as e:
            raise WebRTCMediaError(f'Error handling media track: {str(e)}', peer_id) from e

    async def _handle_transcript(self, transcript: str, peer_id: str) -> None:
        """Handle transcript text with data channel readiness check"""
        try:
            peer = self.peer_session_manager.get_peer(peer_id)
            if not peer:
                logger.warning(f'Peer {peer_id} not foundwhen trying to send transcript')
                return

            if not peer.data_channel:
                logger.warning(
                    f'No data channel available for peer {peer_id}, transcript will be queued'
                )
                # If audio_loop exists, let it handle the queuing
                if peer.audio_loop:
                    peer.audio_loop._pending_transcripts.append(transcript)
                return

            logger.debug(f'Data channel state for peer {peer_id}: {peer.data_channel.readyState}')
            logger.debug(f'Data channel label for peer {peer_id}: {peer.data_channel.label}')

            # Wait for data channel to be open with timeout
            max_wait_time = 5.0  # 5 seconds timeout
            wait_start = time.time()

            while peer.data_channel.readyState != 'open':
                if time.time() - wait_start > max_wait_time:
                    logger.warning(
                        f'Data channel failed to open within {max_wait_time}s '
                        f'for peer {peer_id}, state: {peer.data_channel.readyState}'
                    )
                    # Queue the transcript for later
                    if peer.audio_loop:
                        peer.audio_loop._pending_transcripts.append(transcript)
                    return

                logger.debug(
                    f'Waiting for data channel to open for peer {peer_id}, '
                    f'current state: {peer.data_channel.readyState}'
                )
                await asyncio.sleep(0.1)  # Wait 100ms before checking again

                # Re-check if peer still exists
                peer = self.peer_session_manager.get_peer(peer_id)
                if not peer or not peer.data_channel:
                    logger.warning(
                        f'Peer or data channel disappeared while waiting for peer {peer_id}'
                    )
                    return

            # Now the data channel should be open
            message = json.dumps({'transcript': transcript})
            logger.debug(f'Sending message to peer {peer_id}: {message}')
            peer.data_channel.send(message)
            logger.info(f'Sent transcript to peer {peer_id}: {transcript}')

        except Exception as e:
            logger.error(f'Error sending transcript to peer {peer_id}: {e}', exc_info=True)
            # On error, queue the transcript for retry if possible
            peer = self.peer_session_manager.get_peer(peer_id)
            if peer and peer.audio_loop:
                peer.audio_loop._pending_transcripts.append(transcript)

    async def create_peer_connection(self, peer_id: str) -> None:
        """Create a new peer connection"""
        await self.peer_session_manager.create_peer(peer_id)

    async def close_peer_connection(self, peer_id: str) -> None:
        """Close a peer connection"""
        try:
            # Get peer object
            peer = self.peer_session_manager.get_peer(peer_id)
            if peer:
                # peer.cleanup() will automatically clean up audio_loop
                # Close Peer connection (this will call peer.cleanup())
                await self.peer_session_manager.close_peer(peer_id)

                # Clean up event manager
                webrtc_event_manager.remove_peer_manager(peer_id)

        except Exception as e:
            raise WebRTCPeerError(f'Error closing peer connection: {str(e)}', peer_id) from e

    def get_event_manager(self, peer_id: str) -> PeerEventManager | None:
        """Get event manager for a specific peer"""
        return webrtc_event_manager.get_peer_manager(peer_id)


def get_webrtc_service() -> WebRTCService:
    """
    Get WebRTC service instance

    Returns:
        WebRTCService: Global instance of WebRTC service
    """
    if not hasattr(get_webrtc_service, '_instance'):
        get_webrtc_service._instance = WebRTCService()
    return get_webrtc_service._instance
