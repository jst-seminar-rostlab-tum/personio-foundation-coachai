import asyncio
import fractions
import logging
import re
import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, Optional, Union

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
from app.services.openai_model_service import OpenAI, connect_openai

AUDIO_PTIME = 0.02
AUDIO_BITRATE = 16000

MODEL_SERVICE = 'openai'

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
    model_service: str = MODEL_SERVICE

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
    ai_session: Optional[Union[Gemini, OpenAI]] = None
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
            logger.info(f'Started {self.config.model_service.upper()} connection task')

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
        logger.info(
            f'Connection started for peer {self.peer_id} using {self.config.model_service.upper()}'
        )

        @self.pc.on('datachannel')
        def on_datachannel(channel: RTCDataChannel) -> None:
            self.datachannel = channel
            logger.info(f'Data channel opened for peer {self.peer_id}')

            @channel.on('message')
            async def on_message(message: str) -> None:
                logger.info(f'Received message from peer {self.peer_id}: {message}')
                if self.ai_session:
                    await self.ai_session.send(message)

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

            @track.on('ended')
            async def on_ended() -> None:
                logger.info(f'Track {track.kind} ended for peer {self.peer_id}')

        async def run_recv_audio_track() -> None:
            while self.pc and self.pc.connectionState != 'closed':
                try:
                    frame = await self.recv_audio_track.recv()
                    # print(f'Received frame for peer {self.peer_id}: {frame}')
                    if not self.ai_session:
                        continue
                    await self.ai_session.send(frame)

                except asyncio.CancelledError:
                    logger.info(f'recv_audio_track cancelled for peer {self.peer_id}')
                    break
                except Exception as e:
                    logger.error(f'Error receiving frame for peer {self.peer_id}: {e}')
                    break

        async def run_send_track() -> None:
            timestamp = 0
            buffer = b''
            while self.pc and self.pc.connectionState != 'closed':
                try:
                    async for frame in self.ai_session.audio_frame_consumer():
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
                except asyncio.CancelledError:
                    logger.info(f'send_track cancelled for peer {self.peer_id}')
                    break
                except Exception as e:
                    logger.error(f'Error in send track for peer {self.peer_id}: {e}')
                    # Briefly wait and then continue
                    await asyncio.sleep(0.1)

        async def run_audio_receiver() -> None:
            while self.pc and self.pc.connectionState != 'closed':
                try:
                    if self.ai_session:
                        await self.ai_session.audio_receiver()
                    else:
                        await asyncio.sleep(0.1)
                except asyncio.CancelledError:
                    logger.info(f'audio_receiver cancelled for peer {self.peer_id}')
                    break
                except Exception as e:
                    logger.error(f'Error in audio receiver for peer {self.peer_id}: {e}')
                    # If an error occurs, briefly wait and then retry
                    await asyncio.sleep(0.5)
                    break  # Exit the loop after an error

        async def run_input_transcription_processor() -> None:
            """Process input transcription queue"""
            while self.pc and self.pc.connectionState != 'closed':
                if self.ai_session and hasattr(self.ai_session, '_input_transcription_queue'):
                    try:
                        input_transcription = await asyncio.wait_for(
                            self.ai_session._input_transcription_queue.get(), timeout=1.0
                        )

                        if (
                            self.datachannel
                            and self.datachannel.readyState == 'open'
                            and input_transcription
                        ):
                            self.datachannel.send(
                                WebRTCDataChannelMessage(
                                    role=GeminiUserType.USER, text=input_transcription
                                ).model_dump_json()
                            )

                    except TimeoutError:
                        continue  # Continue the loop after timeout
                    except asyncio.CancelledError:
                        logger.info(
                            f'input_transcription_processor cancelled for peer {self.peer_id}'
                        )
                        break
                    except Exception as e:
                        logger.error(
                            f'Error processing input transcription for peer {self.peer_id}: {e}'
                        )
                        await asyncio.sleep(0.1)

        async def run_output_transcription_processor() -> None:
            """Process output transcription queue"""
            while self.pc and self.pc.connectionState != 'closed':
                if self.ai_session and hasattr(self.ai_session, '_output_transcription_queue'):
                    try:
                        output_transcription = await asyncio.wait_for(
                            self.ai_session._output_transcription_queue.get(), timeout=1.0
                        )
                        logger.debug(f'Output transcription: {output_transcription}')

                        if (
                            self.datachannel
                            and self.datachannel.readyState == 'open'
                            and output_transcription
                        ):
                            self.datachannel.send(
                                WebRTCDataChannelMessage(
                                    role=GeminiUserType.ASSISTANT, text=output_transcription
                                ).model_dump_json()
                            )

                    except TimeoutError:
                        continue  # Continue the loop after timeout
                    except asyncio.CancelledError:
                        logger.info(
                            f'output_transcription_processor cancelled for peer {self.peer_id}'
                        )
                        break
                    except Exception as e:
                        logger.error(
                            f'Error processing output transcription for peer {self.peer_id}: {e}'
                        )
                        await asyncio.sleep(0.1)

        async def monitor_queues() -> None:
            """Monitor queue status"""
            while self.pc and self.pc.connectionState != 'closed':
                try:
                    if (
                        self.ai_session
                        and hasattr(self.ai_session, '_audio_queue')
                        and hasattr(self.ai_session, '_input_transcription_queue')
                        and hasattr(self.ai_session, '_output_transcription_queue')
                    ):
                        audio_queue_size = self.ai_session._audio_queue.qsize()
                        input_queue_size = self.ai_session._input_transcription_queue.qsize()
                        output_queue_size = self.ai_session._output_transcription_queue.qsize()

                        if audio_queue_size > 0 or input_queue_size > 0 or output_queue_size > 0:
                            logger.debug(
                                f'Queue status for peer {self.peer_id}: '
                                f'audio={audio_queue_size}, '
                                f'input_transcription={input_queue_size}, '
                                f'output_transcription={output_queue_size}'
                            )

                    await asyncio.sleep(2)  # Monitor queues every 2 seconds

                except asyncio.CancelledError:
                    logger.info(f'monitor_queues cancelled for peer {self.peer_id}')
                    break
                except Exception as e:
                    logger.error(f'Error monitoring queues for peer {self.peer_id}: {e}')
                    await asyncio.sleep(2)

        try:
            # Connect to model service
            if self.config.model_service == 'openai':
                logger.info(f'Connecting to OpenAI for peer {self.peer_id}...')
                async with connect_openai() as session:
                    logger.info(f'Connected to OpenAI session for peer {self.peer_id}')
                    self.ai_session: OpenAI = session

                    # Create task list
                    tasks = [
                        asyncio.create_task(run_recv_audio_track()),
                        asyncio.create_task(run_audio_receiver()),
                        asyncio.create_task(run_send_track()),
                        asyncio.create_task(run_input_transcription_processor()),
                        asyncio.create_task(run_output_transcription_processor()),
                        asyncio.create_task(monitor_queues()),
                    ]

                    try:
                        await asyncio.gather(*tasks, return_exceptions=True)
                    except asyncio.CancelledError:
                        logger.info(f'OpenAI tasks cancelled for peer {self.peer_id}')
                        # Cancel all tasks
                        for task in tasks:
                            if not task.done():
                                task.cancel()
                        # Wait for all tasks to finish cancellation
                        await asyncio.gather(*tasks, return_exceptions=True)

                    logger.info(f'OpenAI connection finished for peer {self.peer_id}')
            else:  # Default to Gemini
                logger.info(f'Connecting to Gemini for peer {self.peer_id}...')
                async with connect_gemini() as session:
                    logger.info(f'Connected to Gemini session for peer {self.peer_id}')
                    self.ai_session: Gemini = session

                    # Create task list
                    tasks = [
                        asyncio.create_task(run_recv_audio_track()),
                        asyncio.create_task(run_audio_receiver()),
                        asyncio.create_task(run_send_track()),
                        asyncio.create_task(run_input_transcription_processor()),
                        asyncio.create_task(run_output_transcription_processor()),
                        asyncio.create_task(monitor_queues()),
                    ]

                    try:
                        await asyncio.gather(*tasks, return_exceptions=True)
                    except asyncio.CancelledError:
                        logger.info(f'Gemini tasks cancelled for peer {self.peer_id}')
                        # Cancel all tasks
                        for task in tasks:
                            if not task.done():
                                task.cancel()
                        # Wait for all tasks to finish cancellation
                        await asyncio.gather(*tasks, return_exceptions=True)

                    logger.info(f'Gemini connection finished for peer {self.peer_id}')

        except asyncio.CancelledError:
            logger.info(f'Connection cancelled for peer {self.peer_id}')
            raise  # Re-throw the cancellation exception
        except Exception as e:
            logger.error(
                f'Error with {self.config.model_service.upper()} '
                f'session for peer {self.peer_id}: {e}'
            )

        try:
            await self.close()
        except Exception as e:
            logger.error(f'Error closing connection for peer {self.peer_id}: {e}')
        connections.discard(self)
        logger.info(f'Connection stopped for peer {self.peer_id}. Connections {len(connections)}')

    async def close(self) -> None:
        logger.info(f'Closing connection for peer {self.peer_id}')

        # Close RTCPeerConnection
        if self.pc:
            try:
                await asyncio.wait_for(self.pc.close(), timeout=2.0)
            except TimeoutError:
                logger.warning(f'RTCPeerConnection close timed out for peer {self.peer_id}')
            except Exception as e:
                logger.error(f'Error closing RTCPeerConnection for peer {self.peer_id}: {e}')
            finally:
                self.pc = None

        # Close AI session
        if self.ai_session:
            try:
                await asyncio.wait_for(self.ai_session.close(), timeout=2.0)
            except TimeoutError:
                logger.warning(f'AI session close timed out for peer {self.peer_id}')
            except Exception as e:
                logger.error(f'Error closing AI session for peer {self.peer_id}: {e}')
            finally:
                self.ai_session = None

        logger.info(f'Connection closed for peer {self.peer_id}')


@router.post('/offer')
async def offer(request: Request) -> PlainTextResponse:
    connection = RTCConnection()
    connections.add(connection)
    return await connection.handle_offer(request)


@router.post('/offer/{model_name}')
async def offer_with_model(request: Request, model_name: str) -> PlainTextResponse:
    """Use specified model service to create connection"""
    if model_name.lower() not in ['gemini', 'openai']:
        raise ValueError(
            f'Unsupported model service: {model_name}. Please use "gemini" or "openai"'
        )

    config = WebRTCConfig(model_service=model_name.lower())
    connection = RTCConnection(config)
    connections.add(connection)
    return await connection.handle_offer(request)


async def on_shutdown() -> None:
    logger.info(f'Shutting down WebRTC connections. Active connections: {len(connections)}')
    if connections:
        # Create close tasks
        close_tasks = [conn.close() for conn in list(connections)]
        try:
            # Set timeout to avoid infinite waiting
            await asyncio.wait_for(
                asyncio.gather(*close_tasks, return_exceptions=True), timeout=5.0
            )
        except TimeoutError:
            logger.warning('Connection shutdown timed out')
        except Exception as e:
            logger.error(f'Error during shutdown: {e}')

        connections.clear()
    logger.info('WebRTC shutdown complete')
