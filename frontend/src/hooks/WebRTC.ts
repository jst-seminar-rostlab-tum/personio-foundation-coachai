import { useCallback, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { sessionService } from '@/services/SessionService';
import { showErrorToast } from '@/lib/toast';
import { SessionStatus } from '@/interfaces/models/Session';
import { api } from '@/services/ApiClient';
import { MessageSender } from '@/interfaces/models/Simulation';
import { useMessageReducer } from './MessageReducer';
import { useMediaStream } from './MediaStream';

export function useWebRTC(sessionId: string) {
  const { localStreamRef, startStream, stopStream } = useMediaStream();
  const { messages, addPlaceholderMessage, appendDeltaToLastMessage, setMessages } =
    useMessageReducer();

  const [isMicActive, setIsMicActive] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [isDataChannelReady, setIsDataChannelReady] = useState(false);
  const remoteAudioRef = useRef<HTMLAudioElement | null>(null);
  const peerConnectionRef = useRef<RTCPeerConnection | null>(null);
  const dataChannelRef = useRef<RTCDataChannel | null>(null);
  const cleanupRef = useRef<boolean | null>(null);
  const hasInitializedRef = useRef(false);
  const router = useRouter();
  const t = useTranslations('Simulation');

  const cleanup = useCallback(() => {
    if (cleanupRef.current) return;
    cleanupRef.current = true;
    peerConnectionRef.current?.close();
    peerConnectionRef.current = null;
    stopStream();
    if (remoteAudioRef.current) remoteAudioRef.current.srcObject = null;
    setIsMicActive(false);
    setIsConnected(false);
    setIsDataChannelReady(false);
    setMessages([]);
  }, [stopStream, setMessages]);

  const disconnect = useCallback(async () => {
    cleanup();
    cleanupRef.current = false;
    hasInitializedRef.current = false;
    try {
      const { data } = await sessionService.updateSession(api, sessionId, {
        status: SessionStatus.COMPLETED,
      });
      router.push(`/feedback/${data.id}`);
    } catch (err) {
      showErrorToast(err, t('sessionEndError'));
    }
  }, [cleanup, sessionId, router, t]);

  const initWebRTC = useCallback(async () => {
    if (hasInitializedRef.current) return;
    hasInitializedRef.current = true;

    try {
      cleanupRef.current = false;
      const localStream = await startStream();
      setIsMicActive(true);

      const pc = new RTCPeerConnection();
      peerConnectionRef.current = pc;
      localStream.getTracks().forEach((track) => pc.addTrack(track, localStream));

      pc.ontrack = (e) => {
        if (e.track.kind === 'audio' && remoteAudioRef.current) {
          const [stream] = e.streams;
          remoteAudioRef.current.srcObject = stream;
        }
      };

      const dc = pc.createDataChannel('oai-events');
      dataChannelRef.current = dc;
      dc.onopen = () => setIsDataChannelReady(true);
      dc.onclose = () => setIsDataChannelReady(false);
      dc.onerror = () => setIsDataChannelReady(false);

      dc.onmessage = async (event) => {
        try {
          const parsed = JSON.parse(event.data);

          switch (parsed.type) {
            case 'conversation.item.created':
              if (parsed.item.role === 'user' && parsed.item.status === 'completed') {
                addPlaceholderMessage(MessageSender.USER);
              }
              break;

            case 'response.created':
              addPlaceholderMessage(MessageSender.ASSISTANT);
              break;

            case 'conversation.item.input_audio_transcription.delta':
              appendDeltaToLastMessage(MessageSender.USER, parsed.delta);
              break;

            case 'conversation.item.input_audio_transcription.completed':
              await sessionService.createSessionTurn(
                api,
                sessionId,
                MessageSender.USER,
                parsed.transcript,
                '',
                '',
                0,
                0
              );
              break;

            case 'response.audio_transcript.delta':
              appendDeltaToLastMessage(MessageSender.ASSISTANT, parsed.delta);
              break;

            case 'response.audio_transcript.done':
              await sessionService.createSessionTurn(
                api,
                sessionId,
                MessageSender.ASSISTANT,
                parsed.transcript,
                '',
                '',
                0,
                0
              );
              break;

            default:
              // Handle unknown types or ignore
              break;
          }
        } catch {
          // Not JSON – ignore
        }
      };

      pc.onconnectionstatechange = () => {
        if (pc.connectionState === 'connected') setIsConnected(true);
        if (['disconnected', 'failed', 'closed'].includes(pc.connectionState)) disconnect();
      };

      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);
      const sdpText = await sessionService.getSdpResponseTextFromRealtimeApi(
        api,
        sessionId,
        offer.sdp
      );
      await pc.setRemoteDescription({ type: 'answer', sdp: sdpText });
    } catch {
      setIsMicActive(false);
      disconnect();
    }
  }, [disconnect, sessionId, startStream, addPlaceholderMessage, appendDeltaToLastMessage]);

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
