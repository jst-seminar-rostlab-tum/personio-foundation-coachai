from collections.abc import Coroutine
from typing import Any, Callable, Optional, TypeVar

from fastapi import WebSocket

from ...schemas.webrtc_schema import WebRTCMessage

# Define message types
MessageType = TypeVar('MessageType', bound=WebRTCMessage)

# Define message factory type
MessageFactory = Callable[[dict, WebSocket], Coroutine[Any, Any, MessageType]]

# Define signal handler type
SignalHandler = Callable[[MessageType, str], Coroutine[Any, Any, Optional[MessageType]]]
