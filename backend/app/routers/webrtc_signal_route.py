import logging
from typing import Annotated

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from ..schemas.webrtc_schema import WebRTCSignalingMessage
from ..services.websocket_service import WebSocketService, get_websocket_service

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/webrtc', tags=['WebRTC'])


@router.websocket('/signal')
async def websocket_signaling(
    websocket: WebSocket,
    websocket_service: Annotated[WebSocketService, Depends(get_websocket_service)],
) -> None:
    logger.info(f'New WebSocket connection request from: {websocket.client}')
    await websocket.accept()
    logger.info(f'WebSocket connection accepted: {websocket.client}')

    try:
        while True:
            logger.info('Waiting for message...')
            data = await websocket.receive_json()
            logger.debug(f'Received message: {data}')

            signaling_message = WebRTCSignalingMessage(**data)
            logger.debug(f'Parsed message: {signaling_message.model_dump()}')

            await websocket_service.handle_webrtc_message(websocket, signaling_message)
    except WebSocketDisconnect:
        logger.info(f'WebSocket connection closed: {websocket.client}')
    except Exception as e:
        logger.error(f'WebSocket error: {str(e)}')
        logger.exception(e)
        try:
            await websocket.close()
        except Exception as close_error:
            logger.error(f'Error closing WebSocket: {str(close_error)}')
