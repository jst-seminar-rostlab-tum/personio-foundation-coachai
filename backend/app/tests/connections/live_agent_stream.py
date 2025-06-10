"""
## Documentation
Quickstart: https://github.com/google-gemini/cookbook/blob/main/quickstarts/Get_started_LiveAPI.py

## Setup

To install the dependencies for this script, run:

```
pip install google-genai opencv-python pyaudio pillow mss
```
"""

import asyncio
import traceback

import pyaudio
from dotenv import load_dotenv

from app.connections.gemini_client import LIVE_CONFIG, MODEL, get_client

FORMAT = pyaudio.paInt16
CHANNELS = 1
SEND_SAMPLE_RATE = 16000
RECEIVE_SAMPLE_RATE = 24000
CHUNK_SIZE = 1024

load_dotenv()

client = get_client()

pya = pyaudio.PyAudio()


class AudioLoop:
    def __init__(self) -> None:
        self.audio_in_queue = None
        self.out_queue = None

        self.session = None

    async def send_text(self) -> None:
        while True:
            text = await asyncio.to_thread(
                input,
                'message > ',
            )
            if text.lower() == 'q':
                break
            await self.session.send_client_content(
                turns=[
                    {
                        'role': 'user',
                        'parts': [{'text': text or '.'}],
                    },
                ]
            )

    async def send_realtime(self) -> None:
        while True:
            msg = await self.out_queue.get()
            # await self.session.send(input=msg)
            await self.session.send_realtime_input(audio=msg)

    async def listen_audio(self) -> None:
        mic_info = pya.get_default_input_device_info()
        self.audio_stream = await asyncio.to_thread(
            pya.open,
            format=FORMAT,
            channels=CHANNELS,
            rate=SEND_SAMPLE_RATE,
            input=True,
            input_device_index=mic_info['index'],
            frames_per_buffer=CHUNK_SIZE,
        )
        kwargs = {'exception_on_overflow': False} if __debug__ else {}
        while True:
            data = await asyncio.to_thread(self.audio_stream.read, CHUNK_SIZE, **kwargs)
            await self.out_queue.put({'data': data, 'mime_type': 'audio/pcm'})

    async def receive_audio(self) -> None:
        """
        Background task to read from the websocket, log transcripts,
        and write PCM audio chunks to the input queue for playback.
        """
        while True:
            input_transcription = []
            output_transcription = []
            turn = self.session.receive()
            async for response in turn:
                if data := response.data:
                    # Put audio data into the queue for the play_audio task
                    self.audio_in_queue.put_nowait(data)
                    continue
                if text := response.text:
                    print(text, end='')

                if response.server_content.input_transcription:
                    input_transcription.append(response.server_content.input_transcription.text)

                if response.server_content.output_transcription:
                    output_transcription.append(response.server_content.output_transcription.text)

                if response.server_content.interrupted is True:
                    # This indicates the end of the model's turn.
                    # The audio playback should continue until the queue is empty.
                    print('\n>> Gemini finished turn <<')

            # The turn is over, log the full transcript.
            if input_transcription:
                print('\nInput transcript:', ''.join(input_transcription))
            if output_transcription:
                print('Output transcript:', ''.join(output_transcription))

            # Do NOT clear the audio queue here. The play_audio task
            # is responsible for consuming it. Clearing it would cut off playback.

    async def play_audio(self) -> None:
        stream = await asyncio.to_thread(
            pya.open,
            format=FORMAT,
            channels=CHANNELS,
            rate=RECEIVE_SAMPLE_RATE,
            output=True,
        )
        while True:
            bytestream = await self.audio_in_queue.get()
            await asyncio.to_thread(stream.write, bytestream)

    async def run(self) -> None:
        try:
            async with (
                client.aio.live.connect(model=MODEL, config=LIVE_CONFIG) as session,
                asyncio.TaskGroup() as tg,
            ):
                self.session = session

                self.audio_in_queue = asyncio.Queue()
                self.out_queue = asyncio.Queue(maxsize=5)

                send_text_task = tg.create_task(self.send_text())
                tg.create_task(self.send_realtime())
                tg.create_task(self.listen_audio())
                tg.create_task(self.receive_audio())
                tg.create_task(self.play_audio())

                await send_text_task
                raise asyncio.CancelledError('User requested exit')

        except asyncio.CancelledError:
            pass
        except Exception as EG:
            self.audio_stream.close()
            traceback.print_exception(EG)


if __name__ == '__main__':
    main = AudioLoop()
    asyncio.run(main.run())
