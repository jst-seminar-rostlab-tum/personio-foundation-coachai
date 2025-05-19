import argparse
import asyncio
import logging
import os

import httpx
from aiortc import MediaStreamTrack, RTCDataChannel, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRecorder
from aiortc.contrib.signaling import add_signaling_arguments, create_signaling
from dotenv import load_dotenv

ROOT = os.path.dirname(__file__)

# Load environment variables from .env file
load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if OPENAI_API_KEY is None:
    raise ValueError('OPENAI_API_KEY environment variable not set')

OPENAI_BASE_URL = 'https://api.openai.com/v1/realtime'
MODEL_NAME = os.getenv('MODEL_NAME', 'gpt-4o-mini-realtime-preview-2024-12-17')

SESSION_URL = 'http://localhost:8000/session' # Our Session Endpoint to fetch a session token

"""
Initialize a WebRTC session with OpenAI's Realtime API.
This function sets up a WebRTC peer connection,
handles incoming and outgoing audio tracks, and creates a data channel for sending and receiving events.
The function performs the following steps:

1. Get an ephemeral key from your server
2. Create a WebRTC peer connection
3. Set up the audio tracks (incoming and outgoing)
4. Set up a data channel for sending and receiving events
5. Start the session using the Session Description Protocol (SDP)
- Send the SDP offer to the server and receive the SDP answer
- Set the remote description for the peer connection
8. Handle incoming messages on the data channel
9. Handle incoming audio tracks
10. Handle outgoing audio tracks
11. Handle the end of the audio track
12. Handle the end of the WebRTC session

"""
async def init_webrtc_session() -> None:
    async with httpx.AsyncClient() as client:
    
        # 1. Get an ephemeral key from your server
        token_response = await client.get(SESSION_URL)
        token_data = token_response.json()
        ephemeral_key = token_data['client_secret']['value']

        # 2. Create a WebRTC peer connection
        pc = RTCPeerConnection()
        # recorder = MediaRecorder(args.record_to) if args.record_to else MediaBlackhole()
        recorder = MediaBlackhole() # Use MediaBlackhole to discard incoming audio

        # 3. Set up the audio
        # Incoming audio: play remote audio from the model
        @pc.on('track') # This event is triggered when a new track is received
        async def on_track(track: MediaStreamTrack) -> None:
            print(f'Track received: {track.kind}')
            await recorder.start()
            recorder.addTrack(track)

            @track.on('ended')
            async def on_ended() -> None:
                print(f'Track {track.kind} ended')
                await recorder.stop()

        # Outgoing audio: send local microphone audio to the peer
        player = MediaPlayer(os.path.join(ROOT, '../short-fireing-example.wav')) # Replace with your audio source
        pc.addTrack(player.audio)

        # Set up data channel for sending and receiving events
        data_channel = pc.createDataChannel('oai-events')

        @data_channel.on('open')
        def on_open() -> None:
            print(f'{data_channel.label} Data channel opened!')
            # optional: Send initial message
            data_channel.send('Hello from client!')

        @data_channel.on('message')
        def on_message(message: str) -> None:
            print(f'Message received on data channel: {message}')
            # data_channel.send(f'Echo: {message}')

        # incoming data channel
        @pc.on('datachannel')
        def on_datachannel(channel: RTCDataChannel) -> None:
            print(f'Data channel created: {channel.label}')

            @channel.on('message')
            def on_message(message: str) -> None:
                print(f'Message received on data channel: {message}')
                channel.send(f'Echo: {message}')
                # Realtime server events appear here!

        @pc.on('connectionstatechange')
        async def on_connectionstatechange() -> None:
            print('Connection state changed:', pc.connectionState)
            if pc.connectionState == 'failed':
                await pc.close()
                # pcs.discard(pc)

        # 4. Start the session using the Session Description Protocol (SDP)
        offer = await pc.createOffer()
        await pc.setLocalDescription(offer)

        print('SDP Offer: ' + offer.sdp)

        sdp_url = f'{OPENAI_BASE_URL}?model={MODEL_NAME}'
        sdp_response = await client.post(
            sdp_url, 
            content=offer.sdp,
            headers={
                'Authorization': f'Bearer {ephemeral_key}',
                'Content-Type': 'application/sdp'
            })
        
        sdp_answer = sdp_response.text
        print('SDP Answer: ' + sdp_answer)

        answer = RTCSessionDescription(sdp=sdp_answer, type='answer')
        await pc.setRemoteDescription(answer)

if __name__ == '__main__':
    asyncio.run(init_webrtc_session())

# Once you have connected to the Realtime API through either WebRTC or WebSocket, 
# you can call a Realtime model (such as gpt-4o-realtime-preview) to have speech-to-speech conversations. 
# Doing so will require you to send client events to initiate actions, 
# and listen for server events to respond to actions taken by the Realtime API.

# A Realtime Session is a stateful interaction between the model and a connected client. The key components of the session are:
# - The Session object, which controls the parameters of the interaction, like the model being used, the voice used to generate output, and other configuration.
# - A Conversation, which represents user input Items and model output Items generated during the current session.
# - Responses, which are model-generated audio or text Items that are added to the Conversation.