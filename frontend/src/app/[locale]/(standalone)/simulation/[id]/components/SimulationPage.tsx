'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { SessionStatus } from '@/interfaces/Session';
import { sessionService } from '@/services/client/SessionService';
import { useTranslations } from 'next-intl';
import { showErrorToast } from '@/lib/toast';
import SimulationHeader from './SimulationHeader';
import SimulationFooter from './SimulationFooter';
import SimulationRealtimeSuggestions from './SimulationRealtimeSuggestions';
import SimulationMessages, { Message } from './SimulationMessages';

interface SimulationPageComponentProps {
  sessionId: string;
}

function useOpenAIRealtimeWebRTC(sessionId: string) {
  const [isMicActive, setIsMicActive] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [isDataChannelReady, setIsDataChannelReady] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const remoteAudioRef = useRef<HTMLAudioElement | null>(null);
  const peerConnectionRef = useRef<RTCPeerConnection | null>(null);
  const localStreamRef = useRef<MediaStream | null>(null);
  const dataChannelRef = useRef<RTCDataChannel | null>(null);
  const cleanupRef = useRef<boolean | null>(null);
  const router = useRouter();
  const t = useTranslations('Simulation');

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

  const disconnect = useCallback(async () => {
    cleanup();
    cleanupRef.current = false;

    try {
      const { data } = await sessionService.updateSession(sessionId, {
        status: SessionStatus.COMPLETED,
      });
      router.push(`/feedback/${data.id}`);
    } catch (error) {
      showErrorToast(error, t('sessionEndError'));
    }
  }, [cleanup, router, sessionId, t]);

  const initWebRTC = useCallback(async () => {
    try {
      cleanupRef.current = false;
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
      dc.onmessage = async (event) => {
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

          if (parsed.type === 'conversation.item.input_audio_transcription.completed') {
            await sessionService.createSessionTurn(
              sessionId,
              'user',
              parsed.transcript,
              '',
              '',
              0,
              0
            );
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

              return [...prev.slice(0, idx), updatedMsg, ...prev.slice(idx + 1)];
            });
          }

          if (parsed.type === 'response.audio_transcript.done') {
            await sessionService.createSessionTurn(
              sessionId,
              'assistant',
              parsed.transcript,
              '',
              '',
              0,
              0
            );
          }
        } catch {
          // Not JSON, just log
        }
      };

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

      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);
      const sdpResponseText: string = await sessionService.getSdpResponseTextFromRealtimeApi(
        sessionId,
        offer.sdp
      );
      const answer: RTCSessionDescriptionInit = {
        type: 'answer',
        sdp: sdpResponseText,
      };
      await pc.setRemoteDescription(answer);
    } catch {
      setIsMicActive(false);
      disconnect();
    }
  }, [disconnect, sessionId]);

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

export default function SimulationPageComponent({ sessionId }: SimulationPageComponentProps) {
  const [time, setTime] = useState(0);
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
  } = useOpenAIRealtimeWebRTC(sessionId);

  useEffect(() => {
    const interval = setInterval(() => {
      setTime((prev) => prev + 1);
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    initWebRTC();

    return () => {
      cleanup();
    };
  }, [initWebRTC, cleanup, sessionId]);

  const toggleMic = () => {
    if (localStreamRef.current) {
      localStreamRef.current.getAudioTracks().forEach((track) => {
        // eslint-disable-next-line no-param-reassign
        track.enabled = !isMicActive;
      });

      setIsMicActive(!isMicActive);
    }
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
        isMicActive={isMicActive}
        toggleMicrophone={toggleMic}
        isConnected={isConnected && isDataChannelReady}
        onDisconnect={disconnect}
      />
      <audio ref={remoteAudioRef} autoPlay playsInline />
    </div>
  );
}
