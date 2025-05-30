'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import SimulationHeader from '@/components/layout/SimulationHeader';
import SimulationFooter from '@/components/layout/SimulationFooter';
import SimulationRealtimeSuggestions from '@/components/common/SimulationRealtimeSuggestions';
import SimulationMessages from '@/components/common/SimulationMessages';

const RTC_CONFIG = {
  iceServers: [{ urls: 'stun:stun.l.google.com:19302' }, { urls: 'stun:stun1.l.google.com:19302' }],
};

function useWebRTC() {
  const [isMicActive, setIsMicActive] = useState(false);

  const localAudioRef = useRef(null);
  const remoteAudioRef = useRef(null);
  const peerConnectionRef = useRef(null);
  const remotePeerConnectionRef = useRef(null);
  const localStreamRef = useRef(null);
  const cleanupRef = useRef(null);

  const cleanup = useCallback(() => {
    if (cleanupRef.current) return;
    cleanupRef.current = true;

    if (peerConnectionRef.current) {
      peerConnectionRef.current.close();
      peerConnectionRef.current = null;
    }

    if (remotePeerConnectionRef.current) {
      remotePeerConnectionRef.current.close();
      remotePeerConnectionRef.current = null;
    }

    if (localStreamRef.current) {
      localStreamRef.current.getTracks().forEach((track) => {
        track.stop();
      });
      localStreamRef.current = null;
    }

    setIsMicActive(false);
  }, []);

  const initWebRTC = useCallback(async () => {
    try {
      cleanupRef.current = false;

      const localStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });

      localStreamRef.current = localStream;
      setIsMicActive(true);

      if (localAudioRef.current) {
        localAudioRef.current.srcObject = localStream;
      }

      const peerConnection = new RTCPeerConnection(RTC_CONFIG);
      peerConnectionRef.current = peerConnection;

      peerConnection.onconnectionstatechange = () => {
        if (peerConnection.connectionState === 'failed') {
          cleanup();
        }
      };

      localStream.getTracks().forEach((track) => {
        peerConnection.addTrack(track, localStream);
      });

      peerConnection.ontrack = (event) => {
        if (remoteAudioRef.current && event.streams[0]) {
          remoteAudioRef.current.srcObject = event.streams[0];
        }
      };

      const offer = await peerConnection.createOffer();
      await peerConnection.setLocalDescription(offer);

      // Simulate remote peer (for demo - remove in production)
      const remotePeerConnection = new RTCPeerConnection(RTC_CONFIG);
      remotePeerConnectionRef.current = remotePeerConnection;

      peerConnection.onicecandidate = (event) => {
        if (event.candidate) {
          remotePeerConnection.addIceCandidate(event.candidate).catch(console.error);
        }
      };

      remotePeerConnection.onicecandidate = (event) => {
        if (event.candidate) {
          peerConnection.addIceCandidate(event.candidate).catch(console.error);
        }
      };

      localStream.getTracks().forEach((track) => {
        remotePeerConnection.addTrack(track, localStream);
      });

      await remotePeerConnection.setRemoteDescription(offer);
      const answer = await remotePeerConnection.createAnswer();
      await remotePeerConnection.setLocalDescription(answer);
      await peerConnection.setRemoteDescription(answer);
    } catch (err) {
      console.error('WebRTC initialization error:', err);
      setIsMicActive(false);
      cleanup();
    }
  }, [cleanup]);

  return {
    isMicActive,
    setIsMicActive,
    initWebRTC,
    cleanup,
    remoteAudioRef,
  };
}

export default function SimulationPageComponent() {
  const [time, setTime] = useState(0);
  const [isPaused, setIsPaused] = useState(false);
  const { isMicActive, setIsMicActive, initWebRTC, cleanup, remoteAudioRef } = useWebRTC();

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

  return (
    <div className="flex flex-col h-screen">
      <div className="mb-2">
        <SimulationHeader time={time} />
      </div>

      <div className="flex-1 relative p-4 overflow-y-auto mb-4 md:mb-8 [&::-webkit-scrollbar]:hidden [-ms-overflow-style:'none'] [scrollbar-width:'none']">
        <SimulationMessages />
      </div>

      <SimulationRealtimeSuggestions />

      <SimulationFooter
        isPaused={isPaused}
        setIsPaused={setIsPaused}
        isMicActive={isMicActive}
        setIsMicActive={setIsMicActive}
      />
      <audio ref={remoteAudioRef} autoPlay playsInline />
    </div>
  );
}
