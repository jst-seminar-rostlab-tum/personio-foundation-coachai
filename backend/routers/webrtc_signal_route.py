import logging
from typing import Annotated

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from ..schemas.webrtc_schema import WebRTCMessage
from ..services.webrtc_service import WebRTCService, get_webrtc_service

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/webrtc', tags=['WebRTC'])


@router.websocket('/signal')
async def websocket_signaling(
    websocket: WebSocket, webrtc_service: Annotated[WebRTCService, Depends(get_webrtc_service)]
) -> None:
    logger.info(f'New WebSocket connection request from: {websocket.client}')
    await websocket.accept()
    logger.info(f'WebSocket connection accepted: {websocket.client}')

    try:
        while True:
            logger.info('Waiting for message...')
            data = await websocket.receive_json()
            logger.debug(f'Received message: {data}')

            signaling_message = WebRTCMessage(**data)
            logger.debug(f'Parsed message: {signaling_message.model_dump()}')

            response = await webrtc_service.handle_signaling(signaling_message, websocket)
            if response:
                logger.debug(f'Sending response: {response.model_dump()}')
                await websocket.send_json(response.dict())
    except WebSocketDisconnect:
        logger.info(f'WebSocket connection closed: {websocket.client}')
        await webrtc_service.cleanup(websocket)
    except Exception as e:
        logger.error(f'WebSocket error: {str(e)}')
        logger.exception(e)
        await webrtc_service.cleanup(websocket)
