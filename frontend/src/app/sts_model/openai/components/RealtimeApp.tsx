import { useEffect, useRef, useState } from 'react';
import EventLog, { EventType } from './EventLog';
import SessionControls from './SessionControls';

/*
 * This file is part of the OpenAI Realtime App.
 *
 * The OpenAI Realtime App is a web application that allows users to interact with OpenAI's
 * Realtime API using WebRTC for audio and data streaming.
 *
 * The code in this file defines the main component of the application, which manages the
 * WebRTC connection, handles events, and provides a user interface for sending messages
 * and controlling the session.
 *
 */

export default function RealtimeApp() {
  const [isSessionActive, setIsSessionActive] = useState<boolean>(false);
  const [events, setEvents] = useState<EventType[]>([]);
  const [dataChannel, setDataChannel] = useState<RTCDataChannel | null>(null);
  const peerConnection = useRef<RTCPeerConnection | null>(null);
  const audioElement = useRef<HTMLAudioElement | null>(null);

  async function startSession() {
    const tokenResponse = await fetch('http://localhost:7000/session');
    const data = await tokenResponse.json();
    const EPHEMERAL_KEY: string = data.client_secret.value;

    console.warn('Token Response:', data);

    const pc = new RTCPeerConnection();
    console.warn('PeerConnection:', pc);

    audioElement.current = document.createElement('audio');
    audioElement.current.autoplay = true;
    pc.ontrack = (e: RTCTrackEvent) => {
      if (audioElement.current) {
        const [stream] = e.streams;
        audioElement.current.srcObject = stream;
      }
    };

    const ms = await navigator.mediaDevices.getUserMedia({ audio: true });
    pc.addTrack(ms.getTracks()[0]);

    const dc = pc.createDataChannel('oai-events');
    console.warn('DataChannel:', dc);
    setDataChannel(dc);

    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);
    console.warn('Offer:', offer);

    const baseUrl = 'https://api.openai.com/v1/realtime';
    const model = 'gpt-4o-mini-realtime-preview-2024-12-17';
    const sdpResponse = await fetch(`${baseUrl}?model=${model}`, {
      method: 'POST',
      body: offer.sdp,
      headers: {
        Authorization: `Bearer ${EPHEMERAL_KEY}`,
        'Content-Type': 'application/sdp',
      },
    });

    const response = await sdpResponse.text();
    console.warn('SDP Response:', response);

    const answer: RTCSessionDescriptionInit = {
      type: 'answer',
      sdp: response,
    };
    await pc.setRemoteDescription(answer);

    peerConnection.current = pc;
  }

  function stopSession() {
    if (dataChannel) {
      dataChannel.close();
      console.warn('Data channel closed');
    }

    if (peerConnection.current) {
      peerConnection.current.getSenders().forEach((sender) => {
        if (sender.track) {
          sender.track.stop();
        }
      });
      peerConnection.current.close();
      console.warn('Peer connection closed');
    }

    setIsSessionActive(false);
    setDataChannel(null);
    peerConnection.current = null;
  }

  function sendClientEvent(message: EventType): void {
    if (dataChannel) {
      const timestamp = new Date().toLocaleTimeString();
      const eventToSend = {
        ...message,
        event_id: message.event_id || crypto.randomUUID(),
      };

      dataChannel.send(JSON.stringify(message));
      console.warn('Sent event:', eventToSend);

      if (!eventToSend.timestamp) {
        eventToSend.timestamp = timestamp;
      }

      setEvents((prev) => [eventToSend, ...prev]);
    } else {
      console.error('Failed to send message - no data channel available', message);
    }
  }

  function sendTextMessage(message: string): void {
    const event: EventType = {
      type: 'conversation.item.create',
      item: {
        type: 'message',
        role: 'user',
        content: [
          {
            type: 'input_text',
            text: message,
          },
        ],
      },
    };

    sendClientEvent(event);
    sendClientEvent({ type: 'response.create' });
  }

  useEffect(() => {
    if (dataChannel) {
      dataChannel.addEventListener('message', (e: MessageEvent) => {
        const event: EventType = JSON.parse(e.data);
        if (!event.timestamp) {
          event.timestamp = new Date().toLocaleTimeString();
        }
        setEvents((prev) => [event, ...prev]);
        console.warn('Received event:', event);
      });

      dataChannel.addEventListener('open', () => {
        setIsSessionActive(true);
        console.warn('Data channel opened');
        setEvents([]);
      });
    }
  }, [dataChannel]);

  return (
    <>
      <nav className="absolute top-0 left-0 right-0 h-16 flex items-center">
        <div className="flex items-center gap-4 w-full m-4 pb-2 border-0 border-b border-solid border-gray-200">
          <h1>Realtime Console</h1>
        </div>
      </nav>
      <main className="absolute top-16 left-0 right-0 bottom-0">
        <section className="absolute top-0 left-0 right-0 bottom-32 px-4 overflow-y-auto">
          <EventLog events={events} />
        </section>
        <section className="absolute h-32 left-0 right-0 bottom-0 p-4">
          <SessionControls
            startSession={startSession}
            stopSession={stopSession}
            sendClientEvent={sendClientEvent}
            sendTextMessage={sendTextMessage}
            events={events}
            isSessionActive={isSessionActive}
          />
        </section>
      </main>
    </>
  );
}
