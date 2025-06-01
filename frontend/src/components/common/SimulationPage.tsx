'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import SimulationHeader from '@/components/layout/SimulationHeader';
import SimulationFooter from '@/components/layout/SimulationFooter';
import SimulationRealtimeSuggestions from '@/components/common/SimulationRealtimeSuggestions';
import SimulationMessages from '@/components/common/SimulationMessages';

const RTC_CONFIG = {
  iceServers: [{ urls: 'stun:stun.l.google.com:19302' }, { urls: 'stun:stun1.l.google.com:19302' }],
};

const WS_URL = 'ws://localhost:8000/webrtc/signal';

function useWebRTC() {
  const [isMicActive, setIsMicActive] = useState(false);
  const [isConnected, setIsConnected] = useState(false);

  const localAudioRef = useRef(null);
  const remoteAudioRef = useRef(null);
  const peerConnectionRef = useRef(null);
  const localStreamRef = useRef(null);
  const wsRef = useRef(null);
  const cleanupRef = useRef(null);

  const cleanup = useCallback(() => {
    if (cleanupRef.current) return;
    cleanupRef.current = true;

    if (peerConnectionRef.current) {
      peerConnectionRef.current.close();
      peerConnectionRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    if (localStreamRef.current) {
      localStreamRef.current.getTracks().forEach((track) => {
        track.stop();
      });
      localStreamRef.current = null;
    }

    setIsMicActive(false);
    setIsConnected(false);
  }, []);

  const initWebRTC = useCallback(async () => {
    try {
      cleanupRef.current = false;

        // Get local audio stream
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

      // Create WebSocket connection
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket connected');
      };

      ws.onclose = () => {
        console.log('WebSocket closed');
        cleanup();
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        cleanup();
      };

      // Create PeerConnection
      const peerConnection = new RTCPeerConnection(RTC_CONFIG);
      peerConnectionRef.current = peerConnection;

      peerConnection.onconnectionstatechange = () => {
        console.log('Connection state:', peerConnection.connectionState);
        if (peerConnection.connectionState === 'failed') {
          cleanup();
        }
      };

      // Add local audio track
      localStream.getTracks().forEach((track) => {
        peerConnection.addTrack(track, localStream);
      });

      // Handle remote audio track
      peerConnection.ontrack = (event) => {
        if (remoteAudioRef.current && event.streams[0]) {
          remoteAudioRef.current.srcObject = event.streams[0];
        }
      };

      // Handle ICE candidate
      peerConnection.onicecandidate = (event) => {
        if (event.candidate) {
          ws.send(JSON.stringify({
            type: 'candidate',
            candidate: {
              candidate: event.candidate.candidate,
              sdpMid: event.candidate.sdpMid,
              sdpMLineIndex: event.candidate.sdpMLineIndex,
            },
          }));
        }
      };

      // Create and send offer
      const offer = await peerConnection.createOffer();
      await peerConnection.setLocalDescription(offer);
      ws.send(JSON.stringify({
        type: 'offer',
        sdp: offer.sdp,
      }));

      // Handle WebSocket message
      ws.onmessage = async (event) => {
        const message = JSON.parse(event.data);
        console.log('Received message:', message);

        switch (message.type) {
          case 'answer':
            await peerConnection.setRemoteDescription(new RTCSessionDescription({
              type: 'answer',
              sdp: message.sdp,
            }));
            setIsConnected(true);
            break;

          case 'candidate':
            if (message.candidate) {
              await peerConnection.addIceCandidate(new RTCIceCandidate({
                candidate: message.candidate.candidate,
                sdpMid: message.candidate.sdpMid,
                sdpMLineIndex: message.candidate.sdpMLineIndex,
              }));
            }
            break;
        }
      };

    } catch (err) {
      console.error('WebRTC initialization error:', err);
      setIsMicActive(false);
      cleanup();
    }
  }, [cleanup]);

  return {
    isMicActive,
    setIsMicActive,
    isConnected,
    initWebRTC,
    cleanup,
    remoteAudioRef,
  };
}

export default function SimulationPageComponent() {
  const [time, setTime] = useState(0);
  const [isPaused, setIsPaused] = useState(false);
  const { isMicActive, setIsMicActive, isConnected, initWebRTC, cleanup, remoteAudioRef } = useWebRTC();

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
        isConnected={isConnected}
      />
      <audio ref={remoteAudioRef} autoPlay playsInline />
    </div>
  );
}
