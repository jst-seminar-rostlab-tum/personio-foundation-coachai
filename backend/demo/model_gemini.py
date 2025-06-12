import contextlib
from typing import AsyncGenerator, AsyncIterator, Union
from google import genai
from av import AudioFrame, AudioResampler
from PIL.Image import Image
import io
import logging
from logging import getLogger
from abc import abstractmethod
from gemini_client import get_client, MODEL, LIVE_CONFIG
import json

SAMPLE_RATE = 16000
AUDIO_PTIME = 0.02

Input = Union[str, AudioFrame, Image]
Output = Union[AudioFrame]

log_info = getLogger(__name__).info

class Model:
    @abstractmethod
    async def send(self, _input: Input):
        pass

    @abstractmethod
    async def recv(self) -> AsyncIterator[Output]:
        pass

    async def close(self):
        pass

class Gemini(Model):
    def __init__(self, session, rtc_connection):
        self.session = session
        self.rtc_connection = rtc_connection
        self.resampler = AudioResampler(
            format="s16",
            layout="mono",
            rate=SAMPLE_RATE,
            frame_size=int(SAMPLE_RATE * AUDIO_PTIME),
        )

    async def send(self, input: Input):
        if isinstance(input, str):
            await self.session.send(input=input, end_of_turn=True)
        elif isinstance(input, AudioFrame):
            for frame in self.resampler.resample(input):
                blob = genai.types.BlobDict(
                    data=frame.to_ndarray().tobytes(),
                    mime_type=f"audio/pcm;rate={SAMPLE_RATE}",
                )
                await self.session.send(input=blob)

    async def recv(self) -> AsyncIterator[Output]:
        turn = self.session.receive()
        output_transcriptions = []
        async for response in turn:
            if response.data is None:
                # log_info(f"Server Message - {response}")
                if response.server_content.output_transcription:
                    if self.rtc_connection.datachannel is not None and self.rtc_connection.datachannel.readyState == "open" and response.server_content.output_transcription.text is not None:
                        log_info(f"Sending transcription - {response.server_content.output_transcription.text}")
                        output_transcriptions.append(response.server_content.output_transcription.text)
                if response.server_content.interrupted is True:
                    log_info("Server interrupted the turn")
                    break
                continue
            mime_type = response.server_content.model_turn.parts[0].inline_data.mime_type
            sample_rate = int(mime_type.split("rate=")[1])

            frame = AudioFrame(format="s16", layout="mono", samples=len(response.data) / 2)
            frame.sample_rate = sample_rate
            frame.planes[0].update(response.data)
            yield frame
        full_text = " ".join(output_transcriptions).strip()
        if full_text and self.rtc_connection.datachannel and self.rtc_connection.datachannel.readyState == "open":
            await self.rtc_connection.datachannel.send(json.dumps({'message': full_text}))

    async def close(self):
        if self.session is None:
            return
        await self.session.close()
        self.session = None


client = get_client()


@contextlib.asynccontextmanager
async def connect_gemini(rtc_connection) -> AsyncGenerator[Gemini, None]:
    async with client.aio.live.connect(
        model=MODEL,
        config=LIVE_CONFIG,
    ) as session:
        yield Gemini(session, rtc_connection)
