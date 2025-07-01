import { useCallback, useRef, useState } from 'react';
import { useTranslations } from 'next-intl';
import { sessionService } from '@/services/SessionService';
import { showErrorToast } from '@/lib/toast';
import { MessageSender } from '@/interfaces/models/Session';
import { api } from '@/services/ApiClient';
import { useMessageReducer } from './useMessageReducer';
import { useMediaStream } from './useMediaStream';
import { useElapsedTime } from './useElapsedTime';
import { useLocalAudioRecorder } from './useLocalAudioRecorder';
import { useRemoteAudioRecorder } from './useRemoteAudioRecorder';

export function useWebRTC(sessionId: string) {
  const { localStreamRef, startStream, stopStream } = useMediaStream();
  const {
    messages,
    addPlaceholderMessage,
    appendDeltaToLastMessage,
    setMessages,
    getLastMessageStartOffsetMsBySender,
  } = useMessageReducer();

  const { elapsedTimeS, elapsedTimeMsRef, startTimer, stopTimer } = useElapsedTime();

  const { startLocalRecording, stopLocalRecording, extractSegment, localAudioUrls } =
    useLocalAudioRecorder();

  const { startRemoteRecording, stopRemoteRecording, remoteAudioUrls } = useRemoteAudioRecorder();

  const [isMicActive, setIsMicActive] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [isDataChannelReady, setIsDataChannelReady] = useState(false);

  const remoteAudioRef = useRef<HTMLAudioElement | null>(null);
  const peerConnectionRef = useRef<RTCPeerConnection | null>(null);
  const dataChannelRef = useRef<RTCDataChannel | null>(null);
  const cleanupRef = useRef<boolean | null>(null);
  const hasInitializedRef = useRef(false);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const inputAudioBufferSpeechStartedOffsetMsRef = useRef<number>(0);

  // const router = useRouter();
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
    intervalRef.current = null;
  }, [stopStream, setMessages]);

  const disconnect = useCallback(async () => {
    cleanup();
    cleanupRef.current = false;
    hasInitializedRef.current = false;
    try {
      /* const { data } = await sessionService.updateSession(api, sessionId, {
        status: SessionStatus.COMPLETED,
      });
      router.push(`/feedback/${data.id}`); */
    } catch (err) {
      showErrorToast(err, t('sessionEndError'));
    }
  }, [cleanup, t]);

  const initWebRTC = useCallback(async () => {
    if (hasInitializedRef.current) return;
    hasInitializedRef.current = true;

    try {
      cleanupRef.current = false;
      const localStream = await startStream();
      setIsMicActive(true);

      const pc = new RTCPeerConnection();
      peerConnectionRef.current = pc;
      localStream.getTracks().forEach((track: MediaStreamTrack) => pc.addTrack(track, localStream));

      pc.ontrack = (e) => {
        if (e.track.kind === 'audio' && remoteAudioRef.current) {
          const [stream] = e.streams;
          remoteAudioRef.current.srcObject = stream;
        }
      };

      const dc = pc.createDataChannel('oai-events');
      dataChannelRef.current = dc;
      dc.onopen = () => {
        setIsDataChannelReady(true);
        startLocalRecording(localStream);
        startTimer();
      };
      dc.onclose = () => {
        setIsDataChannelReady(false);
        stopLocalRecording();
        stopRemoteRecording();
        stopTimer();
      };
      dc.onerror = () => {
        setIsDataChannelReady(false);
        stopLocalRecording();
        stopRemoteRecording();
        stopTimer();
      };

      dc.onmessage = async (event) => {
        try {
          const parsed = JSON.parse(event.data);

          switch (parsed.type) {
            case 'conversation.item.created':
              if (parsed.item.role === 'user' && parsed.item.status === 'completed') {
                addPlaceholderMessage(MessageSender.USER, elapsedTimeMsRef.current);
              }
              break;

            case 'response.created':
              addPlaceholderMessage(MessageSender.ASSISTANT, elapsedTimeMsRef.current);
              break;

            case 'conversation.item.input_audio_transcription.delta':
              appendDeltaToLastMessage(MessageSender.USER, parsed.delta);
              break;

            case 'conversation.item.input_audio_transcription.completed':
              await sessionService.createSessionTurn(api, {
                sessionId,
                speaker: MessageSender.USER,
                text: parsed.transcript,
                startOffsetMs: getLastMessageStartOffsetMsBySender(MessageSender.USER) ?? 0,
                endOffsetMs: elapsedTimeMsRef.current,
                audioUri: '',
                aiEmotion: '',
              });
              break;

            case 'response.audio_transcript.delta':
              appendDeltaToLastMessage(MessageSender.ASSISTANT, parsed.delta);
              break;

            case 'response.audio_transcript.done':
              await sessionService.createSessionTurn(api, {
                sessionId,
                speaker: MessageSender.ASSISTANT,
                text: parsed.transcript,
                startOffsetMs: getLastMessageStartOffsetMsBySender(MessageSender.ASSISTANT) ?? 0,
                endOffsetMs: elapsedTimeMsRef.current,
                audioUri: '',
                aiEmotion: '',
              });
              break;

            case 'input_audio_buffer.speech_started':
              inputAudioBufferSpeechStartedOffsetMsRef.current = parsed.audio_start_ms;
              stopRemoteRecording();
              break;

            case 'input_audio_buffer.speech_stopped':
              extractSegment(
                inputAudioBufferSpeechStartedOffsetMsRef.current,
                parsed.audio_end_ms,
                elapsedTimeMsRef.current
              );
              break;

            case 'response.content_part.added':
              if (parsed.part.type === 'audio') {
                startRemoteRecording(remoteAudioRef.current?.srcObject as MediaStream);
              }
              break;

            case 'output_audio_buffer.stopped':
              stopRemoteRecording();
              break;

            default:
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
  }, [
    disconnect,
    sessionId,
    startStream,
    addPlaceholderMessage,
    appendDeltaToLastMessage,
    getLastMessageStartOffsetMsBySender,
    elapsedTimeMsRef,
    startTimer,
    stopTimer,
    extractSegment,
    startLocalRecording,
    stopLocalRecording,
    startRemoteRecording,
    stopRemoteRecording,
  ]);

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
    elapsedTimeS,
    localAudioUrls,
    remoteAudioUrls,
  };
}
