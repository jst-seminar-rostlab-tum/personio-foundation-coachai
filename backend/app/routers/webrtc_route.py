import asyncio
import fractions
import logging
import re
import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, Optional

from aiortc import (
    MediaStreamTrack,
    RTCConfiguration,
    RTCDataChannel,
    RTCIceServer,
    RTCPeerConnection,
    RTCSessionDescription,
)
from av import AudioFrame
from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import PlainTextResponse

from app.services.model_gemini import connect_gemini

AUDIO_PTIME = 0.02
AUDIO_BITRATE = 16000

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('webrtc')
connections: set['RTCConnection'] = set()

router = APIRouter(prefix='/webrtc', tags=['WebRTC'])


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    yield
    await on_shutdown()


@dataclass
class WebRTCConfig:
    ice_servers: list[RTCIceServer] = None
    audio_bitrate: int = AUDIO_BITRATE
    audio_ptime: float = AUDIO_PTIME

    def __post_init__(self) -> None:
        if self.ice_servers is None:
            self.ice_servers = [RTCIceServer(urls=['stun:stun.l.google.com:19302'])]


class SendingTrack(MediaStreamTrack):
    kind = 'audio'

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        super().__init__(*args, **kwargs)
        self.queue = asyncio.Queue()

    async def recv(self) -> AudioFrame:
        return await self.queue.get()


class RTCConnection:
    recv_audio_track: Optional[MediaStreamTrack] = None
    recv_video_track: Optional[MediaStreamTrack] = None
    send_track: Optional[SendingTrack] = None
    pc: Optional[RTCPeerConnection] = None
    genai_session: Optional[Any] = None
    datachannel: Optional[RTCDataChannel] = None
    config: WebRTCConfig

    def __init__(self, config: Optional[WebRTCConfig] = None) -> None:
        self.config = config or WebRTCConfig()

    async def handle_offer(self, request: Request) -> PlainTextResponse:
        try:
            content = await request.body()
            # logger.info(f'Received content: {content}')
            offer = RTCSessionDescription(sdp=content.decode(), type='offer')
            # logger.info(f'Created offer: {offer}')

            # logger.info('Creating RTCPeerConnection...')
            self.pc = RTCPeerConnection(RTCConfiguration(iceServers=self.config.ice_servers))
            if not self.pc:
                logger.error('Failed to create RTCPeerConnection')
                raise Exception('Failed to create RTCPeerConnection')
            logger.info(f'Created RTCPeerConnection: {self.pc}')

            # 在这里启动 Gemini 连接
            self._run_task = asyncio.create_task(self._run())
            logger.info('Started Gemini connection task')

            # logger.info('Setting remote description...')
            await self.pc.setRemoteDescription(offer)
            # logger.info('Remote description set successfully')

            # logger.info('Creating answer...')
            answer = await self.pc.createAnswer()
            # logger.info(f'Created answer: {answer}')

            # logger.info('Setting local description...')
            await self.pc.setLocalDescription(answer)
            # logger.info('Local description set successfully')

            sdp = self.pc.localDescription.sdp
            found = re.findall(r'a=rtpmap:(\d+) opus/48000/2', sdp)
            if found:
                sdp = sdp.replace(
                    'opus/48000/2\r\n',
                    'opus/48000/2\r\n'
                    + f'a=fmtp:{found[0]} useinbandfec=1;'
                    + f'usedtx=1;maxaveragebitrate={self.config.audio_bitrate}\r\n',
                )

            return PlainTextResponse(content=sdp, media_type='application/sdp')
        except Exception as e:
            logger.error(f'Error in handle_offer: {str(e)}', exc_info=True)
            raise

    async def _run(self) -> None:
        pc_id = str(uuid.uuid4())

        def log_info(msg: str, *args: Any) -> None:  # noqa: ANN401
            logger.info(f'{pc_id} {msg}', *args)

        log_info('Connection started')

        @self.pc.on('datachannel')
        def on_datachannel(channel: RTCDataChannel) -> None:
            self.datachannel = channel
            log_info('Data channel opened')

            @channel.on('message')
            async def on_message(message: str) -> None:
                log_info(f'Received message: {message}')
                if self.genai_session:
                    await self.genai_session.send(message)

            @channel.on('close')
            def on_close() -> None:
                log_info('Data channel closed')

        @self.pc.on('connectionstatechange')
        async def on_connectionstatechange() -> None:
            if not self.pc:
                return

            log_info('Connection state is %s', self.pc.connectionState)
            if self.pc.connectionState == 'failed' or self.pc.connectionState == 'closed':
                await self.close()

        @self.pc.on('track')
        def on_track(track: MediaStreamTrack) -> None:
            log_info('Track %s received', track.kind)

            if track.kind == 'audio':
                if self.recv_audio_track:
                    return

                self.recv_audio_track = track
                self.send_track = SendingTrack()
                self.pc.addTrack(self.send_track)
                asyncio.ensure_future(run_recv_audio_track())

            @track.on('ended')
            async def on_ended() -> None:
                log_info('Track %s ended', track.kind)

        async def run_recv_audio_track() -> None:
            while True:
                try:
                    frame = await self.recv_audio_track.recv()
                    if not self.genai_session:
                        continue
                    await self.genai_session.send(frame)

                except Exception as e:
                    log_info('Error receiving frame: %s', e)
                    break

        async def run_send_track() -> None:
            timestamp = 0
            buffer = b''
            while self.pc and self.pc.connectionState != 'closed':
                async for frame in self.genai_session.recv():
                    sample_rate = frame.sample_rate
                    samples = int(sample_rate * AUDIO_PTIME)
                    buffer += frame.to_ndarray().tobytes()

                    while len(buffer) / 2 >= samples:
                        frame = AudioFrame(format='s16', layout='mono', samples=samples)
                        frame.sample_rate = sample_rate
                        frame.planes[0].update(buffer[: samples * 2])
                        buffer = buffer[samples * 2 :]

                        timestamp += sample_rate * AUDIO_PTIME
                        frame.pts = timestamp
                        frame.time_base = fractions.Fraction(1, sample_rate)
                        await self.send_track.queue.put(frame)
                        await asyncio.sleep(AUDIO_PTIME)

        try:
            log_info('Connecting to Gemini...')
            async with connect_gemini() as session:
                log_info('Connected to GenAI session')
                self.genai_session = session

                await run_send_track()
                log_info('Connection finished')

        except Exception as e:
            log_info('Error sending frame: %s', e)

        try:
            await self.close()
        except Exception as e:
            log_info('Error closing connection: %s', e)
        connections.discard(self)
        log_info(f'Connection stopped. Connections {len(connections)}')

    async def close(self) -> None:
        if self.pc:
            await self.pc.close()
            self.pc = None
        if self.genai_session:
            await self.genai_session.close()
            self.genai_session = None


@router.post('/offer')
async def offer(request: Request) -> PlainTextResponse:
    connection = RTCConnection()
    connections.add(connection)
    return await connection.handle_offer(request)


async def on_shutdown() -> None:
    coros = [conn.close() for conn in connections]
    await asyncio.gather(*coros)
    connections.clear()
