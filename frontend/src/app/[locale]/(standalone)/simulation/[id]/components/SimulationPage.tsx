'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { useRouter } from 'next/navigation';
// import { api } from '@/services/Api';
import SimulationHeader from './SimulationHeader';
import SimulationFooter from './SimulationFooter';
import SimulationRealtimeSuggestions from './SimulationRealtimeSuggestions';
import SimulationMessages, { Message } from './SimulationMessages';

const MODEL_ID = 'gpt-4o-realtime-preview-2025-06-03';
const mockSessionId = '3fa85f64-5717-4562-b3fc-2c963f66afa6';

function useOpenAIRealtimeWebRTC() {
  const [isMicActive, setIsMicActive] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [isDataChannelReady, setIsDataChannelReady] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);

  const remoteAudioRef = useRef<HTMLAudioElement | null>(null);
  const peerConnectionRef = useRef<RTCPeerConnection | null>(null);
  const localStreamRef = useRef<MediaStream | null>(null);
  const dataChannelRef = useRef<RTCDataChannel | null>(null);
  const cleanupRef = useRef<boolean | null>(null);

  const cleanup = useCallback(() => {
    if (cleanupRef.current) return;
    cleanupRef.current = true;
    if (peerConnectionRef.current) {
      peerConnectionRef.current.close();
      peerConnectionRef.current = null;
    }
    if (localStreamRef.current) {
      localStreamRef.current.getTracks().forEach((track) => track.stop());
      localStreamRef.current = null;
    }
    if (remoteAudioRef.current) {
      remoteAudioRef.current.srcObject = null;
    }
    setIsMicActive(false);
    setIsConnected(false);
    setIsDataChannelReady(false);
    setMessages([]);
  }, []);

  const disconnect = useCallback(() => {
    cleanup();
    cleanupRef.current = false;
  }, [cleanup]);

  const initWebRTC = useCallback(async () => {
    try {
      cleanupRef.current = false;
      // 1. Fetch ephemeral token from your backend
      const tokenResponse = await fetch('http://localhost:8000/realtime-session');
      const data = await tokenResponse.json();
      const EPHEMERAL_KEY = data.client_secret.value;

      // 2. Get local audio stream
      const localStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
        video: false,
      });
      localStreamRef.current = localStream;
      setIsMicActive(true);

      // 3. Create RTCPeerConnection
      const pc = new RTCPeerConnection();
      peerConnectionRef.current = pc;

      // 4. Set up remote audio
      pc.ontrack = (event) => {
        if (event.track.kind === 'audio' && remoteAudioRef.current) {
          const [stream] = event.streams;
          remoteAudioRef.current.srcObject = stream;
        }
      };

      // 5. Add local audio track
      localStream.getTracks().forEach((track) => {
        pc.addTrack(track, localStream);
      });

      // 6. Set up data channel
      const dc = pc.createDataChannel('oai-events');
      dataChannelRef.current = dc;
      dc.onopen = () => {
        setIsDataChannelReady(true);
      };
      dc.onclose = () => {
        setIsDataChannelReady(false);
        dataChannelRef.current = null;
      };
      dc.onerror = () => {
        setIsDataChannelReady(false);
      };
      dc.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data);

          if (
            parsed.type === 'conversation.item.created' &&
            parsed.item.role === 'user' &&
            parsed.item.status === 'completed'
          ) {
            setMessages((prev) => [
              // keep only those that are NOT both empty text and user‐sent
              ...prev.filter((msg) => !(msg.text === '' && msg.sender === 'user')),
              // then append your new (possibly empty) user message
              {
                text: '',
                sender: 'user',
              },
            ]);
          }

          if (parsed.type === 'response.created') {
            setMessages((prev) => [
              // keep only those that are NOT both empty text and user‐sent
              ...prev.filter((msg) => !(msg.text === '' && msg.sender === 'assistant')),
              // then append your new (possibly empty) user message
              {
                text: '',
                sender: 'assistant',
              },
            ]);
          }

          if (parsed.type === 'conversation.item.input_audio_transcription.delta') {
            setMessages((prev) => {
              const idx = prev.findLastIndex((msg) => msg.sender === 'user');
              if (idx === -1) return prev;

              const userMsg = prev[idx];
              const updatedMsg = {
                ...userMsg,
                text: userMsg.text + (parsed.delta ?? ''),
              };

              // Reconstruct the array with the one message replaced
              return [...prev.slice(0, idx), updatedMsg, ...prev.slice(idx + 1)];
            });
          }

          if (parsed.type === 'response.audio_transcript.delta') {
            setMessages((prev) => {
              const idx = prev.findLastIndex((msg) => msg.sender === 'assistant');
              if (idx === -1) return prev;

              const userMsg = prev[idx];
              const updatedMsg = {
                ...userMsg,
                text: userMsg.text + (parsed.delta ?? ''),
              };

              // Reconstruct the array with the one message replaced
              return [...prev.slice(0, idx), updatedMsg, ...prev.slice(idx + 1)];
            });
          }
        } catch {
          // Not JSON, just log
        }
      };

      // 7. Connection state handlers
      pc.onconnectionstatechange = () => {
        if (pc.connectionState === 'connected') {
          setIsConnected(true);
        } else if (
          pc.connectionState === 'disconnected' ||
          pc.connectionState === 'failed' ||
          pc.connectionState === 'closed'
        ) {
          disconnect();
        }
      };

      // 8. Create offer and set local description
      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);

      // 9. Send offer SDP to OpenAI Realtime API
      const baseUrl = 'https://api.openai.com/v1/realtime';
      const sdpResponse = await fetch(`${baseUrl}?model=${MODEL_ID}`, {
        method: 'POST',
        body: offer.sdp,
        headers: {
          Authorization: `Bearer ${EPHEMERAL_KEY}`,
          'Content-Type': 'application/sdp',
        },
      });

      // 10. Set remote description with answer SDP
      const answer = {
        type: 'answer',
        sdp: await sdpResponse.text(),
      };
      await pc.setRemoteDescription(answer);
    } catch {
      setIsMicActive(false);
      disconnect();
    }
  }, [disconnect]);

  return {
    isMicActive,
    setIsMicActive,
    isConnected,
    isDataChannelReady,
    initWebRTC,
    cleanup,
    disconnect,
    remoteAudioRef,
    localStreamRef,
    messages,
  };
}

export default function SimulationPageComponent() {
  const [time, setTime] = useState(0);
  const [isPaused, setIsPaused] = useState(false);
  const {
    isMicActive,
    setIsMicActive,
    isConnected,
    isDataChannelReady,
    initWebRTC,
    cleanup,
    disconnect,
    remoteAudioRef,
    localStreamRef,
    messages,
  } = useOpenAIRealtimeWebRTC();

  const router = useRouter();

  useEffect(() => {
    if (!isPaused) {
      const interval = setInterval(() => {
        setTime((prev) => prev + 1);
      }, 1000);
      return () => clearInterval(interval);
    }
    return undefined;
  }, [isPaused]);

  useEffect(() => {
    initWebRTC();

    return () => {
      cleanup();
    };
  }, [initWebRTC, cleanup]);

  const toggleMic = () => {
    if (localStreamRef.current) {
      localStreamRef.current.getAudioTracks().forEach((track) => {
        // eslint-disable-next-line no-param-reassign
        track.enabled = !isMicActive;
      });
      setIsMicActive(!isMicActive);
    }
  };

  // Log data channel status for debugging
  useEffect(() => {
    console.debug('[WebRTC] Data channel ready status:', isDataChannelReady);
  }, [isDataChannelReady]);

  const handleDisconnect = async () => {
    // await api.post('/session-feedback/', mockFeedback);
    disconnect();
    router.push(`/feedback/${mockSessionId}`);
  };

  return (
    <div className="flex flex-col h-screen">
      <div className="mb-2">
        <SimulationHeader time={time} />
      </div>

      <div className="flex-1 relative p-4 overflow-y-auto mb-4 md:mb-8 [&::-webkit-scrollbar]:hidden [-ms-overflow-style:'none'] [scrollbar-width:'none']">
        <SimulationMessages messages={messages} />
      </div>

      <SimulationRealtimeSuggestions />

      <SimulationFooter
        isPaused={isPaused}
        setIsPaused={setIsPaused}
        isMicActive={isMicActive}
        toggleMicrophone={toggleMic}
        isConnected={isConnected && isDataChannelReady}
        onDisconnect={handleDisconnect}
      />
      <audio ref={remoteAudioRef} autoPlay playsInline />
    </div>
  );
}
