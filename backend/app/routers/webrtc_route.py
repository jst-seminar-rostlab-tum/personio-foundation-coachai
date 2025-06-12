import json
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, HTTPException, WebSocket, WebSocketDisconnect, status
from fastapi.responses import Response

from app.connections.gemini_client import LIVE_CONFIG, get_client

router = APIRouter(prefix='/webrtc', tags=['WebRTC'])
logger = logging.getLogger(__name__)

# 存储活跃的 WebRTC 连接
active_connections: dict[str, WebSocket] = {}


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    yield
    # 关闭所有活跃的 WebRTC 连接
    for connection in active_connections.values():
        await connection.close()
    active_connections.clear()


@router.post('/offer')
async def handle_offer(offer: str) -> Response:
    """
    处理 WebRTC offer 并返回 answer
    """
    try:
        # 获取 Gemini 客户端
        client = get_client()

        # 创建 Gemini 会话
        session = await client.live_connect(
            model='models/gemini-2.0-flash-live-001', config=LIVE_CONFIG
        )

        # 处理 offer 并生成 answer
        # 这里需要实现具体的 WebRTC 信令处理逻辑
        # 返回 answer
        return Response(
            content=json.dumps({'answer': 'your_answer_here'}), media_type='application/json'
        )

    except Exception as e:
        logger.error(f'Error handling WebRTC offer: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.websocket('/ws/{client_id}')
async def websocket_endpoint(websocket: WebSocket, client_id: str) -> None:
    """
    WebSocket 端点用于处理实时音频流
    """
    await websocket.accept()
    active_connections[client_id] = websocket

    try:
        while True:
            # 接收音频数据
            data = await websocket.receive_bytes()

            # 处理音频数据
            # 这里需要实现具体的音频处理逻辑

            # 发送处理后的数据
            await websocket.send_bytes(data)

    except WebSocketDisconnect:
        del active_connections[client_id]
    except Exception as e:
        logger.error(f'Error in WebSocket connection: {e}')
        if client_id in active_connections:
            del active_connections[client_id]
