"""
WebRTC Event Manager

Centralized event management system for WebRTC-related events.
Supports multiple peers and allows different services to register
their own event handlers for WebRTC events.
"""

import asyncio
import logging
from collections.abc import Awaitable, Callable

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

# Event callback types
WebRTCAudioEventCallback = Callable[[WebRTCAudioEvent], Awaitable[None]]
WebRTCSessionEventCallback = Callable[[WebRTCSessionEvent], Awaitable[None]]
WebRTCDataChannelEventCallback = Callable[[WebRTCDataChannelEvent], Awaitable[None]]
WebRTCUserEventCallback = Callable[[WebRTCUserEvent], Awaitable[None]]


class PeerEventManager:
    """Single peer event manager - handles events for one WebRTC peer"""

    def __init__(self, peer_id: str) -> None:
        self.peer_id = peer_id
        self.audio_event_handlers: list[WebRTCAudioEventCallback] = []
        self.session_event_handlers: list[WebRTCSessionEventCallback] = []
        self.data_channel_event_handlers: list[WebRTCDataChannelEventCallback] = []
        self.user_event_handlers: list[WebRTCUserEventCallback] = []

    def add_audio_event_handler(self, handler: WebRTCAudioEventCallback) -> None:
        self.audio_event_handlers.append(handler)

    def add_session_event_handler(self, handler: WebRTCSessionEventCallback) -> None:
        self.session_event_handlers.append(handler)

    def add_data_channel_event_handler(self, handler: WebRTCDataChannelEventCallback) -> None:
        self.data_channel_event_handlers.append(handler)

    def add_user_event_handler(self, handler: WebRTCUserEventCallback) -> None:
        self.user_event_handlers.append(handler)

    async def emit_audio_event(
        self, event_type: WebRTCAudioEventType, data: dict | None = None
    ) -> None:
        event = WebRTCAudioEvent(type=event_type, peer_id=self.peer_id, data=data)
        logger.debug(
            f'[EventManager] Emitting audio event {event_type.value} for peer {self.peer_id}'
        )
        for handler in self.audio_event_handlers:
            try:
                asyncio.create_task(handler(event))
            except Exception as e:
                logger.error(f'[EventManager] Error in audio event handler: {e}')

    async def emit_session_event(
        self, event_type: WebRTCSessionEventType, data: dict | None = None
    ) -> None:
        event = WebRTCSessionEvent(type=event_type, peer_id=self.peer_id, data=data)
        logger.debug(
            f'[EventManager] Emitting session event {event_type.value} for peer {self.peer_id}'
        )
        for handler in self.session_event_handlers:
            try:
                asyncio.create_task(handler(event))
            except Exception as e:
                logger.error(f'[EventManager] Error in session event handler: {e}')

    async def emit_data_channel_event(
        self, event_type: WebRTCDataChannelEventType, data: dict | None = None
    ) -> None:
        event = WebRTCDataChannelEvent(type=event_type, peer_id=self.peer_id, data=data)
        logger.debug(
            f'[EventManager] Emitting data channel event {event_type.value} for peer {self.peer_id}'
        )
        for handler in self.data_channel_event_handlers:
            try:
                asyncio.create_task(handler(event))
            except Exception as e:
                logger.error(
                    f'[EventManager] Error in data channel event handler: {e}',
                    exc_info=True,
                )

    async def emit_user_event(
        self, event_type: WebRTCUserEventType, data: dict | None = None
    ) -> None:
        event = WebRTCUserEvent(type=event_type, peer_id=self.peer_id, data=data)
        logger.info(
            f'[EventManager] Emitting user event {event_type.value} for peer {self.peer_id}, '
            f'handlers count: {len(self.user_event_handlers)}, data: {data}'
        )

        if not self.user_event_handlers:
            logger.warning(
                f'[EventManager] No user event handlers registered for peer {self.peer_id}'
            )
            return

        for i, handler in enumerate(self.user_event_handlers):
            try:
                logger.info(
                    f'[EventManager] Calling user event handler {i + 1}'
                    f'of {len(self.user_event_handlers)}'
                )
                asyncio.create_task(handler(event))
                logger.info(f'[EventManager] User event handler {i + 1} completed successfully')
            except Exception as e:
                logger.error(
                    f'[EventManager] Error in user event handler {i + 1}: {e}',
                    exc_info=True,
                )

    def on_audio_event(
        self, event_type: WebRTCAudioEventType
    ) -> Callable[[WebRTCAudioEventCallback], WebRTCAudioEventCallback]:
        """Decorator to add an audio event handler."""

        def decorator(handler: WebRTCAudioEventCallback) -> WebRTCAudioEventCallback:
            async def wrapped_handler(event: WebRTCAudioEvent) -> None:
                if event.type == event_type:
                    await handler(event)

            self.add_audio_event_handler(wrapped_handler)
            return handler

        return decorator

    def on_session_event(
        self, event_type: WebRTCSessionEventType
    ) -> Callable[[WebRTCSessionEventCallback], WebRTCSessionEventCallback]:
        """Decorator to add a session event handler."""

        def decorator(handler: WebRTCSessionEventCallback) -> WebRTCSessionEventCallback:
            async def wrapped_handler(event: WebRTCSessionEvent) -> None:
                if event.type == event_type:
                    await handler(event)

            self.add_session_event_handler(wrapped_handler)
            return handler

        return decorator

    def on_data_channel_event(
        self, event_type: WebRTCDataChannelEventType
    ) -> Callable[[WebRTCDataChannelEventCallback], WebRTCDataChannelEventCallback]:
        """Decorator to add a data channel event handler."""

        def decorator(handler: WebRTCDataChannelEventCallback) -> WebRTCDataChannelEventCallback:
            async def wrapped_handler(event: WebRTCDataChannelEvent) -> None:
                if event.type == event_type:
                    await handler(event)

            self.add_data_channel_event_handler(wrapped_handler)
            return handler

        return decorator

    def on_user_event(
        self, event_type: WebRTCUserEventType
    ) -> Callable[[WebRTCUserEventCallback], WebRTCUserEventCallback]:
        """Decorator to add a user event handler."""

        def decorator(handler: WebRTCUserEventCallback) -> WebRTCUserEventCallback:
            async def wrapped_handler(event: WebRTCUserEvent) -> None:
                if event.type == event_type:
                    await handler(event)

            self.add_user_event_handler(wrapped_handler)
            return handler

        return decorator


class WebRTCEventManager:
    """Central WebRTC event manager - manages events for all peers"""

    def __init__(self) -> None:
        self.peer_managers: dict[str, PeerEventManager] = {}

    def get_or_create_peer_manager(self, peer_id: str) -> PeerEventManager:
        """Get or create event manager for a specific peer"""
        if peer_id not in self.peer_managers:
            self.peer_managers[peer_id] = PeerEventManager(peer_id)
            logger.info(f'[WebRTCEventManager] Created event manager for peer {peer_id}')
        return self.peer_managers[peer_id]

    def get_peer_manager(self, peer_id: str) -> PeerEventManager | None:
        """Get event manager for a specific peer (returns None if not exists)"""
        return self.peer_managers.get(peer_id)

    def remove_peer_manager(self, peer_id: str) -> None:
        """Remove event manager for a specific peer"""
        if peer_id in self.peer_managers:
            del self.peer_managers[peer_id]
            logger.info(f'[WebRTCEventManager] Removed event manager for peer {peer_id}')

    def get_all_peer_ids(self) -> list[str]:
        """Get all active peer IDs"""
        return list(self.peer_managers.keys())

    def get_handler_counts(self, peer_id: str) -> dict[str, int] | None:
        """Get handler counts for a specific peer"""
        peer_manager = self.get_peer_manager(peer_id)
        if not peer_manager:
            return None

        return {
            'audio': len(peer_manager.audio_event_handlers),
            'session': len(peer_manager.session_event_handlers),
            'data_channel': len(peer_manager.data_channel_event_handlers),
            'user': len(peer_manager.user_event_handlers),
        }


# Global WebRTC event manager instance
webrtc_event_manager = WebRTCEventManager()


def get_webrtc_event_manager() -> WebRTCEventManager:
    """Get the global WebRTC event manager instance"""
    return webrtc_event_manager
