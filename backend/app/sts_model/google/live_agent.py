import asyncio
import io
import os
import wave
from collections.abc import AsyncGenerator, AsyncIterable
from typing import Any

import librosa
import soundfile as sf
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.live import AsyncSession

ROOT = os.path.dirname(__file__)


async def async_enumerate(
    aiterable: AsyncIterable[Any], start: int = 0
) -> AsyncGenerator[tuple[int, Any], None]:
    idx = start
    async for item in aiterable:
        yield idx, item
        idx += 1


# Load environment variables from .env file
load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Establish a connection to the Google Live Agent API
if GEMINI_API_KEY is None:
    raise ValueError('GEMINI_API_KEY environment variable not set')

client = genai.Client(api_key=GEMINI_API_KEY)

model = 'gemini-2.0-flash-live-001'
config = types.LiveConnectConfig(
    system_instruction=types.Content(
        parts=[
            types.Part(
                text='You are a employee and you are talking to your manager. '
                + 'You are a bad employee so the manager is angry at you. '
                + "You are trying to convince the manager that you're a good employee"
                + "and he shouldn't fire you."
            )
        ]
    ),
    response_modalities=['AUDIO'],
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name='Fenrir')
        ),
        language_code='en-US',  # TODO: set in user interface
        # Supported languages: https://ai.google.dev/gemini-api/docs/live#supported-languages
    ),
    realtime_input_config={
        'automatic_activity_detection': {'disabled': True},
        'activity_handling': 'NO_INTERRUPTION',
    },
    input_audio_transcription={},
    output_audio_transcription={},
)


async def send_text_message(message: str, session: AsyncSession) -> None:
    await session.send_client_content(
        turns={'role': 'user', 'parts': [{'text': message}]}, turn_complete=True
    )
    print(f'Sent message: {message}')
    print(f'Sent message: {message}')

    async for response in session.receive():
        if response.text is not None:
            print(response.text, end='')


# You can send audio by converting it to 16-bit PCM, 16kHz, mono format.
async def send_audio_message(session: AsyncSession) -> None:
    # -- Load input audio file --
    input_audio_file_path = os.path.join(ROOT, '../short-fireing-example.wav')

    buffer = io.BytesIO()
    y, sr = librosa.load(input_audio_file_path, sr=16000)
    sf.write(buffer, y, sr, format='RAW', subtype='PCM_16')
    buffer.seek(0)
    audio_bytes = buffer.read()

    print(f'Audio bytes length: {len(audio_bytes)}')

    # If already in correct format, you can use this:
    # audio_bytes = Path("sample.pcm").read_bytes()

    # -- Prepare output audio file --
    output_audio_file_path = os.path.join(ROOT, 'output.wav')

    # Use a context manager to open the wave file
    with wave.open(output_audio_file_path, 'wb') as wf:  # Save the audio response to a file
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)

        # -- Send audio message --
        await session.send_realtime_input(activity_start=types.ActivityStart())
        await session.send_realtime_input(
            audio=types.Blob(data=audio_bytes, mime_type='audio/pcm;rate=16000')
        )
        await session.send_realtime_input(activity_end=types.ActivityEnd())
        print('Sent audio message')

        input_transcription = []
        output_transcription = []

        async for _idx, response in async_enumerate(session.receive()):
            if response.data is not None:
                wf.writeframes(response.data)

            # Print audio data info
            # if response.server_content.model_turn is not None:
            #     print(response.server_content.model_turn.parts[0].inline_data.mime_type)

            # if response.server_content.model_turn:
            # print("Model turn:", response.server_content.model_turn)

            if response.server_content.input_transcription:
                # print("Input transcription:", response.server_content.input_transcription.text)
                input_transcription.append(response.server_content.input_transcription.text)

            if response.server_content.output_transcription:
                # print("Output Transcript:", response.server_content.output_transcription.text)
                output_transcription.append(response.server_content.output_transcription.text)

            if response.server_content.interrupted is True:
                # See: https://ai.google.dev/gemini-api/docs/live#interruptions
                print('Response interrupted')
                break

    print('Audio message sent and response received')

    print('Input:', ''.join(input_transcription))
    print('Output:', ''.join(output_transcription))


async def main() -> None:
    async with client.aio.live.connect(model=model, config=config) as session:
        print('Session started')

        # await send_text_message("Hello World! How are you?", session)

        await send_audio_message(session)


if __name__ == '__main__':
    asyncio.run(main())
