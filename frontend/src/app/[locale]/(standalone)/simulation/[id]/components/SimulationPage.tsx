'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { SimulationPageComponentProps } from '@/interfaces/SimulationPageComponentProps';
import { useRouter } from 'next/navigation';
import { SessionStatus } from '@/interfaces/Session';
import { sessionService } from '@/services/client/SessionService';
import { useTranslations } from 'next-intl';
import { showErrorToast } from '@/lib/toast';
import { webRTCService } from '@/services/client/WebRTCService';
import SimulationHeader from './SimulationHeader';
import SimulationFooter from './SimulationFooter';
import SimulationRealtimeSuggestions from './SimulationRealtimeSuggestions';
import SimulationMessages, { Message } from './SimulationMessages';

function useWebRTCProxy(sessionId: string) {
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

      const pc = new RTCPeerConnection();
      peerConnectionRef.current = pc;

      pc.ontrack = (event) => {
        if (event.track.kind === 'audio' && remoteAudioRef.current) {
          const [stream] = event.streams;
          remoteAudioRef.current.srcObject = stream;
        }
      };

      localStream.getTracks().forEach((track) => {
        pc.addTrack(track, localStream);
      });

      const dc = pc.createDataChannel('data');
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
          if (parsed.role && parsed.text) {
            const sender = parsed.role === 'user' ? 'user' : 'assistant';
            setMessages((prev) => {
              const lastMessage = prev[prev.length - 1];
              if (lastMessage && lastMessage.sender === sender) {
                const updatedMessages = [...prev];
                updatedMessages[updatedMessages.length - 1] = {
                  ...lastMessage,
                  text: parsed.text,
                };
                return updatedMessages;
              }
              return [...prev, { sender, text: parsed.text }];
            });
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

      const offer = await pc.createOffer({
        iceRestart: true,
        offerToReceiveAudio: true,
        offerToReceiveVideo: false,
      });
      await pc.setLocalDescription(offer);
      if (!offer.sdp) {
        throw new Error('Failed to create offer: SDP is undefined');
      }

      const answerSdp = await webRTCService.getAnswerSdp(offer.sdp);

      const answer: RTCSessionDescriptionInit = {
        type: 'answer',
        sdp: answerSdp,
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

export default function SimulationPageComponent({ sessionId }: SimulationPageComponentProps) {
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
  } = useWebRTCProxy(sessionId);

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
        isPaused={isPaused}
        setIsPaused={setIsPaused}
        isMicActive={isMicActive}
        toggleMicrophone={toggleMic}
        isConnected={isConnected && isDataChannelReady}
        onDisconnect={disconnect}
      />
      <audio ref={remoteAudioRef} autoPlay playsInline />
    </div>
  );
}
