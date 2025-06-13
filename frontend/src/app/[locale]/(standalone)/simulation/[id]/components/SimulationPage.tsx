'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { api } from '@/services/Api';
import SimulationHeader from './SimulationHeader';
import SimulationFooter from './SimulationFooter';
import SimulationRealtimeSuggestions from './SimulationRealtimeSuggestions';
import SimulationMessages from './SimulationMessages';

function useWebRTC() {
  const [isMicActive, setIsMicActive] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [isDataChannelReady, setIsDataChannelReady] = useState(false);
  const [receivedTranscripts, setReceivedTranscripts] = useState<{ role: string; text: string }[]>(
    []
  );

  const localAudioRef = useRef<HTMLAudioElement | null>(null);
  const remoteAudioRef = useRef<HTMLAudioElement | null>(null);
  const peerConnectionRef = useRef<RTCPeerConnection | null>(null);
  const localStreamRef = useRef<MediaStream | null>(null);
  const dataChannelRef = useRef<RTCDataChannel | null>(null);
  const pendingMessagesRef = useRef<string[]>([]);
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
    setReceivedTranscripts([]);
    pendingMessagesRef.current = [];
  }, []);

  const disconnect = useCallback(() => {
    console.info('[WebRTC] Disconnecting...');
    cleanup();
    cleanupRef.current = false;
  }, [cleanup]);

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
      if (localAudioRef.current) {
        localAudioRef.current.srcObject = localStream;
      }
      const pc = new RTCPeerConnection();
      peerConnectionRef.current = pc;
      const dataChannel = pc.createDataChannel('data', {
        ordered: true,
        maxRetransmits: 3,
        negotiated: false,
      });
      dataChannelRef.current = dataChannel;
      dataChannel.onopen = () => {
        console.info('[WebRTC] Data channel opened');
      };
      dataChannel.onclose = () => {
        console.info('[WebRTC] Data channel closed');
        setIsDataChannelReady(false);
        dataChannelRef.current = null;
      };
      dataChannel.onerror = (error) => {
        console.error('[WebRTC] Data channel error:', error);
        setIsDataChannelReady(false);
      };
      dataChannel.onmessage = (event) => {
        console.debug('[WebRTC] Received message:', event.data);
        try {
          const parsed = JSON.parse(event.data);
          if (parsed.role && parsed.text) {
            setReceivedTranscripts((prev) => [...prev, { role: parsed.role, text: parsed.text }]);
          }
        } catch {
          console.warn('[WebRTC] Failed to parse message as JSON:', event.data);
        }
      };

      pc.onconnectionstatechange = () => {
        console.info('[WebRTC] Connection state changed:', pc.connectionState);
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
      pc.oniceconnectionstatechange = () => {
        console.info('[WebRTC] ICE connection state changed:', pc.iceConnectionState);
      };

      pc.ontrack = (event) => {
        console.info('[WebRTC] Received remote track:', event.track.kind);
        if (event.track.kind === 'audio' && remoteAudioRef.current) {
          const [firstStream] = event.streams;
          remoteAudioRef.current.srcObject = firstStream;
        }
      };
      localStream.getTracks().forEach((track) => {
        pc.addTrack(track, localStream);
      });
      const offer = await pc.createOffer({
        iceRestart: true,
        offerToReceiveAudio: true,
        offerToReceiveVideo: false,
      });
      if (!offer.sdp) throw new Error('Failed to create offer: SDP is undefined');
      await pc.setLocalDescription(offer);
      // const response = await fetch(`${API_URL}/webrtc/offer`, {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/sdp' },
      //   body: offer.sdp,
      // });
      // const answerSdp = await response.text();
      const response = await api.post('/webrtc/offer', offer.sdp, {
        headers: {
          'Content-Type': 'application/sdp',
        },
        responseType: 'text',
      });
      const answerSdp = response.data;
      await pc.setRemoteDescription(new RTCSessionDescription({ type: 'answer', sdp: answerSdp }));
    } catch (err) {
      console.error('[WebRTC] Initialization error:', err);
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
    dataChannelRef,
    localStreamRef,
    receivedTranscripts,
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
    receivedTranscripts,
  } = useWebRTC();

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

  return (
    <div className="flex flex-col h-screen">
      <div className="mb-2">
        <SimulationHeader time={time} />
      </div>

      <div className="flex-1 relative p-4 overflow-y-auto mb-4 md:mb-8 [&::-webkit-scrollbar]:hidden [-ms-overflow-style:'none'] [scrollbar-width:'none']">
        <SimulationMessages receivedTranscripts={receivedTranscripts} />
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
