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

from app.schemas.webrtc_schema import GeminiUserType, WebRTCDataChannelMessage
from app.services.gemini_model_service import Gemini, connect_gemini

AUDIO_PTIME = 0.02
AUDIO_BITRATE = 16000

connections: set['RTCConnection'] = set()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

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
    peer_id: str

    def __init__(self, config: Optional[WebRTCConfig] = None) -> None:
        self.config = config or WebRTCConfig()
        self.peer_id = str(uuid.uuid4())

    async def handle_offer(self, request: Request) -> PlainTextResponse:
        try:
            content = await request.body()
            offer = RTCSessionDescription(sdp=content.decode(), type='offer')

            self.pc = RTCPeerConnection(RTCConfiguration(iceServers=self.config.ice_servers))
            if not self.pc:
                logger.error('Failed to create RTCPeerConnection')
                raise Exception('Failed to create RTCPeerConnection')
            logger.info(f'Created RTCPeerConnection: {self.pc}')

            self._run_task = asyncio.create_task(self._run())
            logger.info('Started Gemini connection task')

            await self.pc.setRemoteDescription(offer)

            answer = await self.pc.createAnswer()

            await self.pc.setLocalDescription(answer)

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
        logger.info(f'Connection started for peer {self.peer_id}')

        @self.pc.on('datachannel')
        def on_datachannel(channel: RTCDataChannel) -> None:
            self.datachannel = channel
            logger.info(f'Data channel opened for peer {self.peer_id}')

            @channel.on('message')
            async def on_message(message: str) -> None:
                logger.info(f'Received message from peer {self.peer_id}: {message}')
                if self.genai_session:
                    await self.genai_session.send(message)

            @channel.on('close')
            def on_close() -> None:
                logger.info(f'Data channel closed for peer {self.peer_id}')

        @self.pc.on('connectionstatechange')
        async def on_connectionstatechange() -> None:
            if not self.pc:
                return

            logger.info(f'Connection state for peer {self.peer_id} is {self.pc.connectionState}')
            if self.pc.connectionState == 'failed' or self.pc.connectionState == 'closed':
                await self.close()

        @self.pc.on('track')
        def on_track(track: MediaStreamTrack) -> None:
            logger.info(f'Track {track.kind} received for peer {self.peer_id}')

            if track.kind == 'audio':
                if self.recv_audio_track:
                    return

                self.recv_audio_track = track
                self.send_track = SendingTrack()
                self.pc.addTrack(self.send_track)
                asyncio.ensure_future(run_recv_audio_track())

            @track.on('ended')
            async def on_ended() -> None:
                logger.info(f'Track {track.kind} ended for peer {self.peer_id}')

        async def run_recv_audio_track() -> None:
            while True:
                try:
                    frame = await self.recv_audio_track.recv()
                    # print(f'Received frame for peer {self.peer_id}: {frame}')
                    if not self.genai_session:
                        continue
                    await self.genai_session.send(frame)

                except Exception as e:
                    logger.error(f'Error receiving frame for peer {self.peer_id}: {e}')
                    break

        async def run_send_track() -> None:
            timestamp = 0
            buffer = b''
            while self.pc and self.pc.connectionState != 'closed':
                async for frame in self.genai_session.audio_frame_consumer():
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

        async def run_transcription_processor() -> None:
            while self.pc and self.pc.connectionState != 'closed':
                if (
                    self.genai_session
                    and hasattr(self.genai_session, '_output_transcription_queue')
                    and hasattr(self.genai_session, '_input_transcription_queue')
                ):
                    try:
                        input_transcription = (
                            await self.genai_session._input_transcription_queue.get()
                        )
                        output_transcription = (
                            await self.genai_session._output_transcription_queue.get()
                        )
                        if (
                            self.datachannel
                            and self.datachannel.readyState == 'open'
                            and output_transcription
                        ):
                            self.datachannel.send(
                                WebRTCDataChannelMessage(
                                    role=GeminiUserType.USER, text=input_transcription
                                ).model_dump_json()
                            )
                            self.datachannel.send(
                                WebRTCDataChannelMessage(
                                    role=GeminiUserType.ASSISTANT, text=output_transcription
                                ).model_dump_json()
                            )
                    except Exception as e:
                        logger.error(f'Error processing transcription for peer {self.peer_id}: {e}')

        try:
            logger.info(f'Connecting to Gemini for peer {self.peer_id}...')
            async with connect_gemini() as session:
                logger.info(f'Connected to GenAI session for peer {self.peer_id}')
                self.genai_session: Gemini = session

                asyncio.create_task(self.genai_session.audio_receiver())

                await asyncio.gather(
                    run_send_track(),
                    run_transcription_processor(),
                )
                logger.info(f'Connection finished for peer {self.peer_id}')

        except Exception as e:
            logger.error(f'Error sending frame for peer {self.peer_id}: {e}')

        try:
            await self.close()
        except Exception as e:
            logger.error(f'Error closing connection for peer {self.peer_id}: {e}')
        connections.discard(self)
        logger.info(f'Connection stopped for peer {self.peer_id}. Connections {len(connections)}')

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
