import asyncio
import base64
import datetime
import json
import os

import httpx
from aiortc import (
    MediaStreamTrack,
    RTCDataChannel,
    RTCIceCandidate,
    RTCPeerConnection,
    RTCSessionDescription,
)
from aiortc.contrib.media import MediaPlayer, MediaRecorder
from dotenv import load_dotenv

ROOT = os.path.dirname(__file__)

# Load environment variables from .env file
load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if OPENAI_API_KEY is None:
    raise ValueError('OPENAI_API_KEY environment variable not set')

OPENAI_BASE_URL = 'https://api.openai.com/v1/realtime'
MODEL_NAME = os.getenv('MODEL_NAME', 'gpt-4o-mini-realtime-preview-2024-12-17')

# TODO: replace with server URL
SESSION_URL = 'http://localhost:8000/session'  # Our Session Endpoint to fetch a session token


# Send a client event to the Realtime API through the data channel.
def send_client_event(event: dict, data_channel: RTCDataChannel) -> None:
    if not data_channel or data_channel.readyState != 'open':
        print('Data channel is not open. Cannot send event.')
        return

    # Convert the event to a JSON string
    event_json = json.dumps(event)

    # Send the event over the data channel
    data_channel.send(event_json)
    print('Sent client event')


def send_text_message(
    data_channel: RTCDataChannel, text: str = 'Hello World! How are you?'
) -> None:
    event = {
        'type': 'conversation.item.create',
        'item': {
            'type': 'message',
            'role': 'user',
            'content': [
                {
                    'type': 'input_text',
                    'text': text,
                }
            ],
        },
    }
    send_client_event(event, data_channel)

    response_event = {
        'type': 'response.create',
        'response': {
            'modalities': ['text'],
        },
    }
    send_client_event(response_event, data_channel)


def send_audio_message(data_channel: RTCDataChannel) -> None:
    audio_file_path = os.path.join(ROOT, '../short-fireing-example.wav')

    with open(audio_file_path, 'rb') as audio_file:
        audio_bytes = audio_file.read()
        # Convert audio bytes to base64 string
        full_audio = base64.b64encode(audio_bytes).decode('utf-8')

    event = {
        'type': 'conversation.item.create',
        'item': {
            'type': 'message',
            'role': 'user',
            'content': [
                {
                    'type': 'input_audio',
                    'audio': full_audio,
                }
            ],
        },
    }
    send_client_event(event, data_channel)
    send_client_event({'type': 'response.create'}, data_channel)


"""
Initialize a WebRTC session with OpenAI's Realtime API.
This function sets up a WebRTC peer connection,
handles incoming and outgoing audio tracks, and creates a data channel
for sending and receiving events.
The function performs the following steps:

1. Get an ephemeral key from your server
2. Create a WebRTC peer connection
3. Set up the audio tracks (incoming and outgoing)
4. Set up a data channel for sending and receiving events
5. Start the session using the Session Description Protocol (SDP)
- Send the SDP offer to the server and receive the SDP answer
- Set the remote description for the peer connection

"""


async def init_webrtc_session() -> None:
    async with httpx.AsyncClient() as client:
        # 1. Get an ephemeral key from your server
        token_response = await client.get(SESSION_URL)
        token_data = token_response.json()
        ephemeral_key = token_data['client_secret']['value']

        # 2. Create a WebRTC peer connection
        pc = RTCPeerConnection()
        recorder = MediaRecorder(os.path.join(ROOT, 'recorded_audio.wav'))
        # MediaRecorder uses ffmpeg. If ffmpeg is not installed or not in PATH, it won't work.
        # ffmpeg.org/download.html

        # 3. Set up the audio
        # Incoming audio: play remote audio from the model
        @pc.on('track')  # This event is triggered when a new track is received
        async def on_track(track: MediaStreamTrack) -> None:
            print(f'Track received: {track.kind}')
            await recorder.start()
            recorder.addTrack(track)
            print('Recorder started')

            @track.on('ended')
            async def on_ended() -> None:
                print(f'Track {track.kind} ended')
                await recorder.stop()
                print('Recorder stopped')

        # Outgoing audio: send local microphone audio to the peer
        # TODO: replace with audio source from browser

        # Option 1: Use microphone audio
        # player = MediaPlayer(
        #     'audio=Mikrofonarray (Intel® Smart Sound Technologie für digitale Mikrofone)',
        #     format='dshow'
        # )
        # pc.addTrack(player.audio)

        # Option 2: Use a audio file
        player = MediaPlayer(os.path.join(ROOT, '../short-fireing-example.wav'))
        pc.addTrack(player.audio)
        player.audio.on('ended', lambda: print('(MediaPlayer) Audio track ended'))

        # 4. Set up data channel for sending and receiving events
        data_channel = pc.createDataChannel('oai-events')

        @data_channel.on('open')
        def on_open() -> None:
            print(f'{data_channel.label} Data channel opened!')
            # optional: Send initial message
            data_channel.send('Hello from client!')

        @data_channel.on('message')
        async def on_message(message: str) -> None:
            print(f'({data_channel.label}) Message received on data channel: {message}')
            # data_channel.send(f'Echo: {message}')

            # convert the message to a JSON object
            try:
                message = json.loads(message)
            except json.JSONDecodeError:
                print(f'Failed to parse message as JSON: {message}')

            if message.get('type') == 'session.created':
                print('Session created')
                send_client_event(
                    {
                        'type': 'session.update',
                        'session': {
                            'instructions': "Never use the word 'moist' in your responses!"
                        },
                    },
                    data_channel,
                )

            elif message.get('type') == 'input_audio_buffer.speech_started':
                print('Speech started')
                send_audio_message(data_channel)

            elif message.get('type') == 'response.done':
                print('Response done')

            else:
                print(f'Unknown message type: {message.get("type")}')

        # incoming data channel
        @pc.on('datachannel')
        def on_datachannel(channel: RTCDataChannel) -> None:
            print(f'Data channel created: {channel.label}')

            @channel.on('message')
            def on_message(message: str) -> None:
                print(f'({channel.label}) Message received on data channel: {message}')
                channel.send(f'Echo: {message}')
                # Realtime server events appear here!

        @pc.on('connectionstatechange')
        async def on_connectionstatechange() -> None:
            print('Connection state changed:', pc.connectionState)
            if pc.connectionState == 'failed':
                await pc.close()
                # pcs.discard(pc)

        @pc.on('iceconnectionstatechange')
        async def on_iceconnectionstatechange() -> None:
            print('ICE connection state changed:', pc.iceConnectionState)

        @pc.on('icecandidate')
        async def on_icecandidate(candidate: RTCIceCandidate) -> None:
            print('ICE candidate:', candidate)

        @pc.on('signalingstatechange')
        async def on_signalingstatechange() -> None:
            print('Signaling state changed:', pc.signalingState)
            # print timestamp
            print('Timestamp (seconds):', datetime.datetime.now().timestamp())

        # 5. Start the session using the Session Description Protocol (SDP)
        offer = await pc.createOffer()
        await pc.setLocalDescription(offer)

        print('SDP Offer: ' + offer.sdp)

        sdp_url = f'{OPENAI_BASE_URL}?model={MODEL_NAME}'
        sdp_response = await client.post(
            sdp_url,
            content=offer.sdp,
            headers={'Authorization': f'Bearer {ephemeral_key}', 'Content-Type': 'application/sdp'},
        )

        sdp_answer = sdp_response.text
        print('SDP Answer: ' + sdp_answer)

        answer = RTCSessionDescription(sdp=sdp_answer, type='answer')
        await pc.setRemoteDescription(answer)

        # Stay connected until the connection is closed or failed
        try:
            while pc.connectionState not in ['closed', 'failed']:
                await asyncio.sleep(1)

        finally:
            print('Disconnecting...')
            if pc.connectionState == 'connected':
                await pc.close()
            if data_channel.readyState == 'open':
                await data_channel.close()
            await recorder.stop()
            print('Disconnected!')


if __name__ == '__main__':
    asyncio.run(init_webrtc_session())
