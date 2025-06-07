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
import os
import traceback

import pyaudio
from dotenv import load_dotenv
from google import genai
from google.genai import types

FORMAT = pyaudio.paInt16
CHANNELS = 1
SEND_SAMPLE_RATE = 16000
RECEIVE_SAMPLE_RATE = 24000
CHUNK_SIZE = 1024

MODEL = 'models/gemini-2.0-flash-live-001'

# Load environment variables from .env file
load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

client = genai.Client(
    http_options={'api_version': 'v1beta'},
    api_key=GEMINI_API_KEY,
)


CONFIG = types.LiveConnectConfig(
    response_modalities=[
        'AUDIO',
    ],
    media_resolution='MEDIA_RESOLUTION_MEDIUM',
    system_instruction=types.Content(
        parts=[
            types.Part(
                text='Be very angry and aggressive. '
                # text="You are a employee and you are talking to your manager. "
                # + "You are a bad employee so the manager is angry at you."
                # + " Try begging him to not fire you."
            )
        ]
    ),
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name='Puck')
        )
    ),
    realtime_input_config=types.RealtimeInputConfig(
        automatic_activity_detection=types.AutomaticActivityDetection(
            disabled=False,  # default
            start_of_speech_sensitivity=types.StartSensitivity.START_SENSITIVITY_LOW,
            end_of_speech_sensitivity=types.EndSensitivity.END_SENSITIVITY_HIGH,
            prefix_padding_ms=20,
            silence_duration_ms=100,
        ),
    ),
    context_window_compression=types.ContextWindowCompressionConfig(
        trigger_tokens=25600,
        sliding_window=types.SlidingWindow(target_tokens=12800),
    ),
    input_audio_transcription={},
    output_audio_transcription={},
)

pya = pyaudio.PyAudio()


class AudioLoop:
    def __init__(self) -> None:
        self.audio_in_queue = None
        self.out_queue = None

        self.session = None

        self.send_text_task = None
        self.receive_audio_task = None
        self.play_audio_task = None

    async def send_text(self) -> None:
        while True:
            text = await asyncio.to_thread(
                input,
                'message > ',
            )
            if text.lower() == 'q':
                break
            await self.session.send(input=text or '.', end_of_turn=True)

    async def send_realtime(self) -> None:
        while True:
            msg = await self.out_queue.get()
            await self.session.send(input=msg)

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
        "Background task to reads from the websocket and write pcm chunks to the output queue"
        while True:
            input_transcription = []
            output_transcription = []
            turn = self.session.receive()
            async for response in turn:
                if data := response.data:
                    self.audio_in_queue.put_nowait(data)
                    continue
                if text := response.text:
                    print(text, end='')

                if response.server_content.input_transcription:
                    # print("Input Transcript:", response.server_content.input_transcription.text)
                    input_transcription.append(response.server_content.input_transcription.text)

                if response.server_content.output_transcription:
                    # print("Output Transcript:", response.server_content.output_transcription.text)
                    output_transcription.append(response.server_content.output_transcription.text)

                if response.server_content.interrupted is True:
                    # See: https://ai.google.dev/gemini-api/docs/live#interruptions

                    print('Response interrupted')

            print('Input:', ''.join(input_transcription))
            print('Output:', ''.join(output_transcription))

            # If you interrupt the model, it sends a turn_complete.
            # For interruptions to work, we need to stop playback.
            # So empty out the audio queue because it may have loaded
            # much more audio than has played yet.
            while not self.audio_in_queue.empty():
                self.audio_in_queue.get_nowait()

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
                client.aio.live.connect(model=MODEL, config=CONFIG) as session,
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
