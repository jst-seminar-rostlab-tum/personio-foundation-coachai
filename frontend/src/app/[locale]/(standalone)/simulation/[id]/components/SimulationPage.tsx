'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import SimulationHeader from './SimulationHeader';
import SimulationFooter from './SimulationFooter';
import SimulationRealtimeSuggestions from './SimulationRealtimeSuggestions';
import SimulationMessages from './SimulationMessages';
import { WebVoiceProcessor } from '@picovoice/web-voice-processor';

const RTC_CONFIG = {
  iceServers: [{ urls: 'stun:stun.l.google.com:19302' }],
};

const WS_URL = 'ws://localhost:8000/webrtc/signal';

function useWebRTC() {
  const [isMicActive, setIsMicActive] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [isDataChannelReady, setIsDataChannelReady] = useState(false);
  const [receivedTranscripts, setReceivedTranscripts] = useState<string[]>([]);
  const [isSpeaking, setIsSpeaking] = useState(false);

  const localAudioRef = useRef<HTMLAudioElement | null>(null);
  const remoteAudioRef = useRef<HTMLAudioElement | null>(null);
  const peerConnectionRef = useRef<RTCPeerConnection | null>(null);
  const localStreamRef = useRef<MediaStream | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const cleanupRef = useRef<boolean | null>(null);
  const dataChannelRef = useRef<RTCDataChannel | null>(null);
  const pendingMessagesRef = useRef<string[]>([]);
  const voiceProcessorRef = useRef<WebVoiceProcessor | null>(null);

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

    if (voiceProcessorRef.current) {
      voiceProcessorRef.current.stop();
      voiceProcessorRef.current = null;
    }

    setIsMicActive(false);
    setIsConnected(false);
    setIsDataChannelReady(false);
    setReceivedTranscripts([]);
    pendingMessagesRef.current = [];
    setIsSpeaking(false);
  }, []);

  const disconnect = useCallback(() => {
    console.info('[WebRTC] Disconnecting...');
    cleanup();
    cleanupRef.current = false;
  }, [cleanup]);

  // Function to send pending messages when data channel becomes ready
  const sendPendingMessages = useCallback(() => {
    if (dataChannelRef.current && dataChannelRef.current.readyState === 'open') {
      const messages = pendingMessagesRef.current;
      pendingMessagesRef.current = [];

      messages.forEach((message) => {
        try {
          dataChannelRef.current?.send(message);
          console.debug('[WebRTC] Sent pending message:', message);
        } catch (error) {
          console.error('[WebRTC] Error sending pending message:', error);
          // Re-queue the message if sending failed
          pendingMessagesRef.current.push(message);
        }
      });
    }
  }, []);

  // Function to send message (queues if channel not ready)
  const sendDataChannelMessage = useCallback((message: string) => {
    if (dataChannelRef.current && dataChannelRef.current.readyState === 'open') {
      try {
        dataChannelRef.current.send(message);
        console.debug('[WebRTC] Sent message immediately:', message);
      } catch (error) {
        console.error('[WebRTC] Error sending message:', error);
        pendingMessagesRef.current.push(message);
      }
    } else {
      console.debug('[WebRTC] Data channel not ready, queuing message:', message);
      pendingMessagesRef.current.push(message);
    }
  }, []);

  const initVAD = useCallback(async (stream: MediaStream) => {
    try {
      const voiceProcessor = await WebVoiceProcessor.create({
        stream,
        frameLength: 512,
        sampleRate: 16000,
        threshold: 0.5, // Voice detection threshold
        onVoiceStart: () => {
          console.debug('[VAD] Voice detected');
          setIsSpeaking(true);
        },
        onVoiceEnd: () => {
          console.debug('[VAD] Voice ended');
          setIsSpeaking(false);
        },
      });
      voiceProcessorRef.current = voiceProcessor;
      await voiceProcessor.start();
      console.info('[VAD] Voice processor started');
    } catch (error) {
      console.error('[VAD] Failed to initialize voice processor:', error);
    }
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

      // Initialize VAD
      await initVAD(localStream);

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
        console.debug('[WebRTC] Data channel label:', dataChannel.label);
        console.debug('[WebRTC] Data channel id:', dataChannel.id);
        console.debug('[WebRTC] Data channel protocol:', dataChannel.protocol);
        console.debug('[WebRTC] Data channel binaryType:', dataChannel.binaryType);
        console.debug('[WebRTC] Data channel bufferedAmount:', dataChannel.bufferedAmount);
        console.debug('[WebRTC] Data channel ordered:', dataChannel.ordered);
        console.debug('[WebRTC] Data channel maxRetransmits:', dataChannel.maxRetransmits);
        console.debug('[WebRTC] Data channel negotiated:', dataChannel.negotiated);

        // Set up data channel event handlers
        dataChannel.onopen = () => {
          console.info('[WebRTC] Data channel opened, state:', dataChannel.readyState);
          console.info('[WebRTC] Data channel opened, timestamp:', new Date().toISOString());
          setIsDataChannelReady(true);

          // Send any pending messages
          sendPendingMessages();

          try {
            sendDataChannelMessage('test message from client');
            console.debug('[WebRTC] Test message sent');
          } catch (error) {
            console.error('[WebRTC] Error sending test message:', error);
          }
        };

        dataChannel.onclose = () => {
          console.info('[WebRTC] Data channel closed, state:', dataChannel.readyState);
          console.info('[WebRTC] Data channel closed, timestamp:', new Date().toISOString());
          setIsDataChannelReady(false);
          dataChannelRef.current = null;
        };

        dataChannel.onerror = (error) => {
          console.error('[WebRTC] Data channel error:', error);
          console.error('[WebRTC] Data channel error, timestamp:', new Date().toISOString());
          setIsDataChannelReady(false);
        };

        dataChannel.onmessage = (event) => {
          console.debug('[WebRTC] Received message:', event.data);
          console.info('[WebRTC] Received message, timestamp:', new Date().toISOString());
          try {
            const parsed = JSON.parse(event.data);
            console.info('[WebRTC] Parsed server message:', parsed);

            // If it's a transcript message, display it prominently
            if (parsed.transcript) {
              console.info('[WebRTC] TRANSCRIPT RECEIVED:', parsed.transcript);
              setReceivedTranscripts((prev) => [...prev, parsed.transcript]);
            }
          } catch {
            console.warn('[WebRTC] Failed to parse message as JSON:', event.data);
          }
        };

        // Handle incoming data channels
        peerConnection.ondatachannel = (event) => {
          console.info('[WebRTC] Received data channel:', event.channel.label);
          const receivedChannel = event.channel;

          // Don't overwrite the created channel reference
          // Instead, set up handlers for the received channel
          receivedChannel.onopen = () => {
            console.info('[WebRTC] Received channel opened');
            setIsDataChannelReady(true);
            sendPendingMessages();
          };

          receivedChannel.onclose = () => {
            console.info('[WebRTC] Received channel closed');
            setIsDataChannelReady(false);
          };

          receivedChannel.onmessage = (msgEvent) => {
            console.info('[WebRTC] Received message from server:', msgEvent.data);
            try {
              const parsed = JSON.parse(msgEvent.data);
              console.info('[WebRTC] Parsed message:', parsed);
            } catch {
              console.warn('[WebRTC] Failed to parse message as JSON:', msgEvent.data);
            }
          };

          receivedChannel.onerror = (error) => {
            console.error('[WebRTC] Received channel error:', error);
            setIsDataChannelReady(false);
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
  }, [disconnect, sendPendingMessages, sendDataChannelMessage, initVAD]);

  return {
    isMicActive,
    setIsMicActive,
    isConnected,
    isDataChannelReady,
    isSpeaking,
    initWebRTC,
    cleanup,
    disconnect,
    remoteAudioRef,
    dataChannelRef,
    localStreamRef,
    sendPendingMessages,
    sendDataChannelMessage,
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
    isSpeaking,
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
        isSpeaking={isSpeaking}
      />
      <audio ref={remoteAudioRef} autoPlay playsInline />
    </div>
  );
}
