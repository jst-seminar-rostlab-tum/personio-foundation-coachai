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

    if (remoteAudioRef.current) {
      remoteAudioRef.current.srcObject = null;
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

      // Create PeerConnection
      const peerConnection = new RTCPeerConnection(RTC_CONFIG);
      peerConnectionRef.current = peerConnection;

      // 监听连接状态变化
      peerConnection.onconnectionstatechange = () => {
        console.log('[WebRTC] Connection state changed:', peerConnection.connectionState);
        if (peerConnection.connectionState === 'connected') {
          console.log('[WebRTC] Connection established');
        }
      };

      peerConnection.oniceconnectionstatechange = () => {
        console.log('[WebRTC] ICE connection state changed:', peerConnection.iceConnectionState);
        if (peerConnection.iceConnectionState === 'connected') {
          console.log('[WebRTC] ICE connection established');
        }
      };

      peerConnection.onsignalingstatechange = () => {
        console.log('[WebRTC] Signaling state changed:', peerConnection.signalingState);
        if (peerConnection.signalingState === 'stable') {
          console.log('[WebRTC] Signaling stable');
        }
      };

      // 处理接收到的音频流
      peerConnection.ontrack = (event) => {
        console.log('[WebRTC] Received track:', event.track.kind);
        if (event.track.kind === 'audio') {
          console.log('[WebRTC] Received audio track');
          if (remoteAudioRef.current && event.streams[0]) {
            console.log('[WebRTC] Setting remote audio stream');
            remoteAudioRef.current.srcObject = event.streams[0];
          }
        }
      };

      ws.onopen = async () => {
        console.log('[WebRTC] WebSocket connected');
        // Add local audio track
        localStream.getTracks().forEach((track) => {
          peerConnection.addTrack(track, localStream);
        });

        // Handle remote audio track
        peerConnection.ontrack = (event) => {
          console.log('[WebRTC] Received track:', event.track.kind);
          if (event.track.kind === 'audio') {
            console.log('[WebRTC] Received audio track');
            if (remoteAudioRef.current && event.streams[0]) {
              console.log('[WebRTC] Setting remote audio stream');
              remoteAudioRef.current.srcObject = event.streams[0];
            }
          }
        };

        // Handle ICE candidate
        peerConnection.onicecandidate = (event) => {
          if (event.candidate) {
            console.log('[WebRTC] ICE candidate generated:', event.candidate);
            if (ws.readyState === WebSocket.OPEN) {
              ws.send(JSON.stringify({
                type: 'candidate',
                candidate: {
                  candidate: event.candidate.candidate,
                  sdpMid: event.candidate.sdpMid,
                  sdpMLineIndex: event.candidate.sdpMLineIndex,
                },
              }));
              console.log('[WebRTC] ICE candidate sent to server:', {
                candidate: event.candidate.candidate,
                sdpMid: event.candidate.sdpMid,
                sdpMLineIndex: event.candidate.sdpMLineIndex,
              });
            } else {
              console.warn('[WebRTC] ICE candidate generated but WebSocket not open, candidate not sent:', event.candidate);
            }
          } else {
            console.log('[WebRTC] ICE candidate gathering completed (null candidate)');
          }
        };

        // Create and send offer
        const offer = await peerConnection.createOffer();
        console.log('[WebRTC] Created offer SDP:', offer.sdp);
        await peerConnection.setLocalDescription(offer);
        ws.send(JSON.stringify({
          type: 'offer',
          sdp: offer.sdp,
        }));
      };

      ws.onclose = () => {
        console.log('WebSocket closed');
        cleanup();
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        cleanup();
      };

      // Handle WebSocket message
      ws.onmessage = async (event) => {
        const message = JSON.parse(event.data);
        console.log('Received message:', message);

        switch (message.type) {
          case 'answer':
            console.log('[WebRTC] Received answer:', message);
            await peerConnection.setRemoteDescription(new RTCSessionDescription({
              type: 'answer',
              sdp: message.sdp,
            }));
            setIsConnected(true);
            break;

          case 'candidate':
            if (message.candidate) {
              console.log('[WebRTC] Adding ICE candidate:', message.candidate);
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
