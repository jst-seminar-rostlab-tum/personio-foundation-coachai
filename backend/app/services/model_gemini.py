import contextlib
import json
from abc import abstractmethod
from collections.abc import AsyncGenerator, AsyncIterator
from logging import getLogger
from typing import Optional, Protocol, Union

from aiortc import RTCDataChannel, RTCPeerConnection
from av import AudioFrame, AudioResampler
from google import genai
from google.genai import live
from PIL.Image import Image

from app.connections.gemini_client import LIVE_CONFIG, MODEL, get_client

SAMPLE_RATE = 16000
AUDIO_PTIME = 0.02

type Input = Union[str, AudioFrame, Image]
type Output = AudioFrame

log_info = getLogger(__name__).info


class RTCConnection(Protocol):
    datachannel: Optional[RTCDataChannel]
    pc: Optional[RTCPeerConnection]


class Model(Protocol):
    @abstractmethod
    async def send(self, _input: Input) -> None:
        pass

    @abstractmethod
    async def recv(self) -> AsyncIterator[Output]:
        pass

    @abstractmethod
    async def close(self) -> None:
        pass


class Gemini(Model):
    def __init__(
        self,
        session: live.AsyncSession,
        rtc_connection: RTCConnection,
    ) -> None:
        self.session = session
        self.rtc_connection = rtc_connection
        self.resampler = AudioResampler(
            format='s16',
            layout='mono',
            rate=SAMPLE_RATE,
            frame_size=int(SAMPLE_RATE * AUDIO_PTIME),
        )

    async def send(self, input: Input) -> None:
        if isinstance(input, str):
            await self.session.send(input=input, end_of_turn=True)
        elif isinstance(input, AudioFrame):
            for frame in self.resampler.resample(input):
                blob = genai.types.BlobDict(
                    data=frame.to_ndarray().tobytes(),
                    mime_type=f'audio/pcm;rate={SAMPLE_RATE}',
                )
                await self.session.send(input=blob)

    async def recv(self) -> AsyncIterator[Output]:
        turn = self.session.receive()
        output_transcriptions: list[str] = []
        async for response in turn:
            if response.data is not None:
                mime_type = response.server_content.model_turn.parts[0].inline_data.mime_type
                sample_rate = int(mime_type.split('rate=')[1])

                frame = AudioFrame(format='s16', layout='mono', samples=len(response.data) / 2)
                frame.sample_rate = sample_rate
                frame.planes[0].update(response.data)
                yield frame
                continue

            # Handle server content
            if response.server_content.interrupted:
                log_info('Server interrupted the turn')
                break

            # Handle transcription
            if not response.server_content.output_transcription:
                continue

            transcription = response.server_content.output_transcription
            if not transcription.text:
                continue

            if not self.rtc_connection.datachannel:
                continue

            if self.rtc_connection.datachannel.readyState != 'open':
                continue

            transcription_text = transcription.text
            log_info(f'Sending transcription - {transcription_text}')
            output_transcriptions.append(transcription_text)

        # Send final transcription if any
        full_text = ' '.join(output_transcriptions).strip()
        if (
            full_text
            and self.rtc_connection.datachannel
            and self.rtc_connection.datachannel.readyState == 'open'
        ):
            await self.rtc_connection.datachannel.send(json.dumps({'message': full_text}))

    async def close(self) -> None:
        if self.session is None:
            return
        await self.session.close()
        self.session = None


client = get_client()


@contextlib.asynccontextmanager
async def connect_gemini(rtc_connection: RTCConnection) -> AsyncGenerator[Gemini, None]:
    async with client.aio.live.connect(
        model=MODEL,
        config=LIVE_CONFIG,
    ) as session:
        yield Gemini(session, rtc_connection)
