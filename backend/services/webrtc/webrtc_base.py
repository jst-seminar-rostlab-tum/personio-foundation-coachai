import logging
from functools import wraps
from typing import Callable, Optional

from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaBlackhole
from fastapi import WebSocket

from ...schemas.webrtc_schema import (
    WebRTCMessage,
    WebRTCSignalingMessage,
    WebRTCSignalingType,
)
from .types import MessageFactory, MessageType, SignalHandler

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def message_factory(
    message_type: WebRTCSignalingType,
) -> Callable[[MessageFactory], MessageFactory]:
    """
    Decorator to register a message factory

    Args:
        message_type: Type of message to handle
    """

    def decorator(factory: MessageFactory) -> MessageFactory:
        if not hasattr(message_factory, '_factories'):
            message_factory._factories = {}
        message_factory._factories[message_type] = factory
        logger.debug(f'Registered factory for message type: {message_type}')
        return factory

    return decorator


@message_factory(WebRTCSignalingType.OFFER)
@message_factory(WebRTCSignalingType.ANSWER)
@message_factory(WebRTCSignalingType.CANDIDATE)
async def create_signaling_message(data: dict, websocket: WebSocket) -> WebRTCMessage:
    """Create a signaling message"""
    return WebRTCSignalingMessage(**data)


def signal_handler(signal_type: WebRTCSignalingType) -> Callable[[SignalHandler], SignalHandler]:
    """
    Decorator to register a signal handler

    Args:
        signal_type: Type of signal to handle
    """
    logger.debug(f'Registering signal handler for type: {signal_type}')

    def decorator(func: SignalHandler) -> SignalHandler:
        @wraps(func)
        async def wrapper(message: MessageType, peer_id: str) -> Optional[WebRTCSignalingMessage]:
            logger.debug(f'Handler wrapper called for type: {signal_type}')
            return await func(message, peer_id)

        # Register the handler
        if not hasattr(signal_handler, '_handlers'):
            logger.debug('Creating _handlers dictionary')
            signal_handler._handlers = {}
        signal_handler._handlers[signal_type] = wrapper
        logger.debug(f'Registered handler for signal type: {signal_type}')
        logger.debug(f'Current handlers: {list(signal_handler._handlers.keys())}')
        return wrapper

    return decorator


if not hasattr(signal_handler, '_handlers'):
    logger.debug('Initializing signal_handler._handlers')
    signal_handler._handlers = {}


class WebRTCService:
    """WebRTC service with signal handler registration"""

    def __init__(self) -> None:
        """Initialize the WebRTC service with an empty peer connection store"""
        self.peers: dict[str, RTCPeerConnection] = {}
        self.media_blackhole = MediaBlackhole()
        self.signal_handlers: dict[WebRTCSignalingType, SignalHandler] = {}
        self._register_handlers()

    def _register_handlers(self) -> None:
        """Reload all registered handlers"""
        if hasattr(signal_handler, '_handlers'):
            self.signal_handlers.update(signal_handler._handlers)
            logger.debug(f'Reloaded handlers in service: {list(self.signal_handlers.keys())}')

    async def _create_message(
        self, message_type: WebRTCSignalingType, data: MessageType, websocket: WebSocket
    ) -> WebRTCMessage:
        """Create a message instance based on its type"""
        factory = message_factory._factories.get(message_type, create_signaling_message)
        return await factory(data, websocket)

    async def handle_signaling(
        self, message: MessageType, websocket: WebSocket
    ) -> Optional[MessageType]:
        """
        Handle WebRTC signaling messages

        Args:
            message: Signaling message data
            websocket: WebSocket connection

        Returns:
            Optional[MessageType]: Response to be sent to the client
        """
        peer_id = str(id(websocket))
        logger.debug(f'Received message type: {message.type} from peer {peer_id}')
        logger.debug(f'Message data: {message.model_dump()}')
        logger.debug(f'Available handlers: {list(self.signal_handlers.keys())}')

        if message.type == WebRTCSignalingType.OFFER:
            # Create new peer connection
            pc = RTCPeerConnection()
            self.peers[peer_id] = pc
            logger.debug(f'Created new peer connection for peer {peer_id}')

            # Set remote description
            await pc.setRemoteDescription(RTCSessionDescription(sdp=message.sdp, type='offer'))
            logger.debug(f'Set remote description for peer {peer_id}')

            # Create answer
            answer = await pc.createAnswer()
            await pc.setLocalDescription(answer)
            logger.debug(f'Created and set local answer for peer {peer_id}')

            return WebRTCSignalingMessage(
                type=WebRTCSignalingType.ANSWER, sdp=pc.localDescription.sdp
            )

        elif message.type == WebRTCSignalingType.CANDIDATE:
            pc = self.get_peer(peer_id)
            if pc:
                await pc.addIceCandidate(message.candidate)
                logger.debug(f'Added ICE candidate for peer {peer_id}')

        # Handle custom signal types
        elif message.type in self.signal_handlers:
            handler = self.signal_handlers[message.type]
            try:
                logger.debug(f'Found handler for message type: {message.type}')
                if message.type in message_factory._factories:
                    logger.debug('Creating message with factory')
                    message = await self._create_message(
                        message.type, message.model_dump(), websocket
                    )
                logger.debug('Calling handler')
                await handler(message, peer_id)
                return None
            except Exception as e:
                logger.error(f'Error handling message type {message.type}: {e}')
                logger.exception(e)
                return None
        else:
            logger.warning(f'No handler found for message type: {message.type}')

        return None

    async def cleanup(self, websocket: WebSocket) -> None:
        """
        Clean up WebRTC connection

        Args:
            websocket: WebSocket connection to clean up
        """
        peer_id = str(id(websocket))
        if peer_id in self.peers:
            pc = self.peers[peer_id]
            await pc.close()
            del self.peers[peer_id]
            logger.debug(f'Cleaned up peer connection for peer {peer_id}')

    def get_peer(self, peer_id: str) -> Optional[RTCPeerConnection]:
        """
        Get peer connection by ID

        Args:
            peer_id: ID of the peer connection

        Returns:
            Optional[RTCPeerConnection]: Peer connection if exists
        """
        return self.peers.get(peer_id)


def get_webrtc_service() -> WebRTCService:
    """
    Get WebRTC service instance

    Returns:
        WebRTCService: Global instance of WebRTC service
    """
    if not hasattr(get_webrtc_service, '_instance'):
        get_webrtc_service._instance = WebRTCService()
    return get_webrtc_service._instance
