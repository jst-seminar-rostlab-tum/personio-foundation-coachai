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
  const dataChannelRef = useRef(null);
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

  const disconnect = useCallback(() => {
    console.log('[WebRTC] Disconnecting...');
    cleanup();
    cleanupRef.current = false;
  }, [cleanup]);

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

      // Create PeerConnection
      const peerConnection = new RTCPeerConnection(RTC_CONFIG);
      peerConnectionRef.current = peerConnection;

      // Create data channel BEFORE creating offer
      const dataChannel = peerConnection.createDataChannel('transcript', {
        ordered: true,
        maxRetransmits: 3,
        negotiated: false,
        id: 0
      });
      dataChannelRef.current = dataChannel;
      console.log('[WebRTC] Data channel created');

      // Set up data channel event handlers
      dataChannel.onopen = () => {
        console.log('[WebRTC] Data channel opened, state:', dataChannel.readyState);
        // Send test message when channel opens
        dataChannel.send('test message from client');
        console.log('[WebRTC] Test message sent');
      };

      dataChannel.onclose = () => {
        console.log('[WebRTC] Data channel closed, state:', dataChannel.readyState);
      };

      dataChannel.onerror = (error) => {
        console.error('[WebRTC] Data channel error:', error);
      };

      dataChannel.onmessage = (event) => {
        console.log('[WebRTC] Received message:', event.data);
        // Echo the message back to client
        dataChannel.send(`Echo: ${event.data}`);
        console.log('[WebRTC] Echo message sent');
      };

      // Add connection state change handlers
      peerConnection.onconnectionstatechange = () => {
        console.log('[WebRTC] Connection state changed:', peerConnection.connectionState);
        if (peerConnection.connectionState === 'connected') {
          console.log('[WebRTC] Connection established');
          setIsConnected(true);
        } else if (peerConnection.connectionState === 'disconnected' ||
                  peerConnection.connectionState === 'failed' ||
                  peerConnection.connectionState === 'closed') {
          console.log('[WebRTC] Connection lost');
          disconnect();
        }
      };

      peerConnection.oniceconnectionstatechange = () => {
        console.log('[WebRTC] ICE connection state changed:', peerConnection.iceConnectionState);
        if (peerConnection.iceConnectionState === 'connected') {
          console.log('[WebRTC] ICE connection established');
        } else if (peerConnection.iceConnectionState === 'disconnected' || 
                  peerConnection.iceConnectionState === 'failed' || 
                  peerConnection.iceConnectionState === 'closed') {
          console.log('[WebRTC] ICE connection lost');
          disconnect();
        }
      };

      peerConnection.onicegatheringstatechange = () => {
        console.log('[WebRTC] ICE gathering state changed:', peerConnection.iceGatheringState);
      };

      peerConnection.onsignalingstatechange = () => {
        console.log('[WebRTC] Signaling state changed:', peerConnection.signalingState);
        if (peerConnection.signalingState === 'stable') {
          console.log('[WebRTC] Signaling stable');
        }
      };

      // Create WebSocket connection
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = async () => {
        console.log('[WebRTC] WebSocket connected');
        
        // Add local audio track
        localStream.getTracks().forEach((track) => {
          peerConnection.addTrack(track, localStream);
        });

        // Create and send offer
        const offer = await peerConnection.createOffer();
        console.log('[WebRTC] Created offer SDP:', offer.sdp);
        await peerConnection.setLocalDescription(offer);
        ws.send(JSON.stringify({
          type: 'offer',
          sdp: offer.sdp,
        }));
      };

      // Handle ICE candidates
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
            console.log('[WebRTC] ICE candidate sent to server');
          }
        } else {
          console.log('[WebRTC] ICE candidate gathering completed');
        }
      };

      ws.onclose = () => {
        console.log('[WebRTC] WebSocket closed');
        disconnect();
      };

      ws.onerror = (error) => {
        console.error('[WebRTC] WebSocket error:', error);
        disconnect();
      };

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
    initWebRTC,
    cleanup,
    disconnect,
    remoteAudioRef,
    dataChannelRef,
  };
}

export default function SimulationPageComponent() {
  const [time, setTime] = useState(0);
  const [isPaused, setIsPaused] = useState(false);
  const { 
    isMicActive, 
    setIsMicActive, 
    isConnected, 
    initWebRTC, 
    cleanup, 
    disconnect,
    remoteAudioRef 
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
        onDisconnect={disconnect}
      />
      <audio ref={remoteAudioRef} autoPlay playsInline />
    </div>
  );
}
