'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import SimulationHeader from './SimulationHeader';
import SimulationFooter from './SimulationFooter';
import SimulationRealtimeSuggestions from './SimulationRealtimeSuggestions';
import SimulationMessages from './SimulationMessages';

const RTC_CONFIG = {
  iceServers: [{ urls: 'stun:stun.l.google.com:19302' }],
};

const WS_URL = 'ws://localhost:8000/webrtc/signal';

function useWebRTC() {
  const [isMicActive, setIsMicActive] = useState(false);
  const [isConnected, setIsConnected] = useState(false);

  const localAudioRef = useRef<HTMLAudioElement | null>(null);
  const remoteAudioRef = useRef<HTMLAudioElement | null>(null);
  const peerConnectionRef = useRef<RTCPeerConnection | null>(null);
  const localStreamRef = useRef<MediaStream | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const cleanupRef = useRef<boolean | null>(null);
  const dataChannelRef = useRef<RTCDataChannel | null>(null);
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
    console.info('[WebRTC] Disconnecting...');
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

      // Create WebSocket connection first
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = async () => {
        console.info('[WebRTC] WebSocket connected');

        // Add local audio track
        localStream.getTracks().forEach((track) => {
          peerConnection.addTrack(track, localStream);
        });

        // Create data channel BEFORE creating the offer
        const dataChannel = peerConnection.createDataChannel('transcript', {
          ordered: true,
          maxRetransmits: 3,
          negotiated: false,
        });
        dataChannelRef.current = dataChannel;
        console.debug('[WebRTC] Data channel created, state:', dataChannel.readyState);

        // Set up data channel event handlers
        dataChannel.onopen = () => {
          console.info('[WebRTC] Data channel opened, state:', dataChannel.readyState);
          try {
            dataChannel.send('test message from client');
            console.debug('[WebRTC] Test message sent');
          } catch (error) {
            console.error('[WebRTC] Error sending test message:', error);
          }
        };

        dataChannel.onclose = () => {
          console.info('[WebRTC] Data channel closed, state:', dataChannel.readyState);
          dataChannelRef.current = null;
        };

        dataChannel.onerror = (error) => {
          console.error('[WebRTC] Data channel error:', error);
        };

        dataChannel.onmessage = (event) => {
          console.debug('[WebRTC] Received message:', event.data);
          try {
            dataChannel.send(`Echo: ${event.data}`);
            console.debug('[WebRTC] Echo message sent');
          } catch (error) {
            console.error('[WebRTC] Error sending echo message:', error);
          }
        };

        // Handle incoming data channels
        peerConnection.ondatachannel = (event) => {
          console.info('[WebRTC] Received data channel:', event.channel.label);
          const receivedChannel = event.channel;
          dataChannelRef.current = receivedChannel;

          receivedChannel.onopen = () => {
            console.info('[WebRTC] Received channel opened');
          };

          receivedChannel.onclose = () => {
            console.info('[WebRTC] Received channel closed');
            dataChannelRef.current = null;
          };

          receivedChannel.onmessage = (msgEvent) => {
            console.debug('[WebRTC] Received message:', msgEvent.data);
          };
        };

        // Set up connection state handlers
        peerConnection.onconnectionstatechange = () => {
          console.info('[WebRTC] Connection state changed:', peerConnection.connectionState);
          if (peerConnection.connectionState === 'connected') {
            console.info('[WebRTC] Connection established');
            setIsConnected(true);
          } else if (
            peerConnection.connectionState === 'disconnected' ||
            peerConnection.connectionState === 'failed' ||
            peerConnection.connectionState === 'closed'
          ) {
            console.info('[WebRTC] Connection lost');
            disconnect();
          }
        };

        peerConnection.oniceconnectionstatechange = () => {
          console.info('[WebRTC] ICE connection state changed:', peerConnection.iceConnectionState);
        };

        // Add ICE candidate handler
        peerConnection.onicecandidate = (event) => {
          if (event.candidate) {
            console.debug('[WebRTC] New ICE candidate:', {
              candidate: event.candidate.candidate,
              sdpMid: event.candidate.sdpMid,
              sdpMLineIndex: event.candidate.sdpMLineIndex,
              protocol: event.candidate.protocol,
              type: event.candidate.type,
              address: event.candidate.address,
              port: event.candidate.port,
            });
            ws.send(
              JSON.stringify({
                signal_type: 'candidate',
                candidate: event.candidate,
              })
            );
          } else {
            console.info('[WebRTC] ICE candidate gathering completed');
          }
        };

        peerConnection.onicegatheringstatechange = () => {
          console.debug('[WebRTC] ICE gathering state changed:', peerConnection.iceGatheringState);
        };

        // Handle incoming tracks
        peerConnection.ontrack = (event) => {
          console.info('[WebRTC] Received remote track:', event.track.kind);
          if (event.track.kind === 'audio' && remoteAudioRef.current) {
            const [firstStream] = event.streams;
            remoteAudioRef.current.srcObject = firstStream;
          }
        };

        // Create offer after data channel is created
        const offer = await peerConnection.createOffer({
          iceRestart: true,
          offerToReceiveAudio: true,
          offerToReceiveVideo: false,
        });

        if (!offer.sdp) {
          throw new Error('Failed to create offer: SDP is undefined');
        }

        await peerConnection.setLocalDescription(offer);
        ws.send(
          JSON.stringify({
            signal_type: 'offer',
            sdp: offer.sdp,
          })
        );
      };

      // Handle incoming messages from signaling server
      ws.onmessage = async (event) => {
        const message = JSON.parse(event.data);

        if (message.signal_type === 'answer') {
          console.info('[WebRTC] Received answer:', message);
          console.debug('[WebRTC] Answer SDP:', message.sdp);
          await peerConnection.setRemoteDescription(
            new RTCSessionDescription({
              type: 'answer',
              sdp: message.sdp,
            })
          );
        } else if (message.signal_type === 'candidate') {
          console.info('[WebRTC] Received ICE candidate');
          try {
            await peerConnection.addIceCandidate(new RTCIceCandidate(message.candidate));
          } catch (error) {
            console.error('[WebRTC] Error adding ICE candidate:', error);
          }
        }
      };

      ws.onclose = () => {
        console.info('[WebRTC] WebSocket closed');
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
    localStreamRef,
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
    remoteAudioRef,
    localStreamRef,
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
        toggleMicrophone={toggleMic}
        isConnected={isConnected}
        onDisconnect={disconnect}
      />
      <audio ref={remoteAudioRef} autoPlay playsInline />
    </div>
  );
}
