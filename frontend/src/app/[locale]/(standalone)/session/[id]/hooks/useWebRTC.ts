import { useCallback, useRef, useState } from 'react';
import { sessionService } from '@/services/SessionService';
import { ConnectionStatus, MessageSender } from '@/interfaces/models/Session';
import { api } from '@/services/ApiClient';
import { showErrorToast } from '@/lib/utils/toast';
import { useTranslations } from 'next-intl';
import { useMessageReducer } from './useMessageReducer';
import { useMediaStream } from './useMediaStream';
import { useElapsedTime } from './useElapsedTime';
import { useLocalAudioRecorder } from './useLocalAudioRecorder';
import { useRemoteAudioRecorder } from './useRemoteAudioRecorder';
import { useSessionTurns } from './useSessionTurns';
import { useSessionLiveFeedback } from './useSessionLiveFeedback';

export function useWebRTC(sessionId: string) {
  const t = useTranslations('Session');

  const { localStreamRef, startStream, stopStream, isMicActive, toggleMic } = useMediaStream();

  const { messages, addPlaceholderMessage, appendDeltaToLastMessage } = useMessageReducer();

  const { elapsedTimeS, elapsedTimeMsRef, startTimer, stopTimer } = useElapsedTime();

  const { startLocalRecording, stopLocalRecording, extractSegment } =
    useLocalAudioRecorder(localStreamRef);

  const { startRemoteRecording, stopRemoteRecording } = useRemoteAudioRecorder();

  const { addAudioToTurn, addMetadataToTurn, addStartOffsetMsToTurn, addEndOffsetMsToTurn } =
    useSessionTurns();

  const { stopGetLiveFeedbackInterval, startGetLiveFeedbackInterval, sessionLiveFeedbacks } =
    useSessionLiveFeedback(sessionId);

  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>(
    ConnectionStatus.Connecting
  );

  const remoteAudioRef = useRef<HTMLAudioElement | null>(null);
  const peerConnectionRef = useRef<RTCPeerConnection | null>(null);
  const dataChannelRef = useRef<RTCDataChannel | null>(null);
  const cleanupRef = useRef<boolean>(false);
  const hasInitializedRef = useRef<boolean>(false);

  const inputAudioBufferSpeechStartedOffsetMsRef = useRef<number>(0);
  const remoteResponseIdRef = useRef<string | null>(null);

  const cleanup = useCallback(() => {
    if (cleanupRef.current) return;
    cleanupRef.current = true;
    peerConnectionRef.current?.close();
    peerConnectionRef.current = null;
    stopStream();
    stopLocalRecording();
    stopRemoteRecording();
    if (remoteAudioRef.current) remoteAudioRef.current.srcObject = null;
    setConnectionStatus(ConnectionStatus.Disconnected);
    hasInitializedRef.current = false;
    stopTimer();
    stopGetLiveFeedbackInterval();
  }, [stopStream, stopLocalRecording, stopRemoteRecording, stopTimer, stopGetLiveFeedbackInterval]);

  const initWebRTC = useCallback(async () => {
    if (hasInitializedRef.current) return;
    hasInitializedRef.current = true;

    cleanupRef.current = false;

    const pc = new RTCPeerConnection();
    peerConnectionRef.current = pc;

    pc.onconnectionstatechange = () => {
      const state = pc.connectionState as ConnectionStatus;

      if (state !== ConnectionStatus.New) {
        setConnectionStatus(state);
      }
      if (state === ConnectionStatus.Failed || state === ConnectionStatus.Closed) {
        cleanup();
      }
    };

    await startStream();
    localStreamRef.current
      ?.getTracks()
      .forEach((track: MediaStreamTrack) => pc.addTrack(track, localStreamRef.current!));

    pc.ontrack = (e) => {
      if (e.track.kind === 'audio' && remoteAudioRef.current) {
        const [stream] = e.streams;
        remoteAudioRef.current.srcObject = stream;
      }
    };

    const dc = pc.createDataChannel('oai-events');
    dataChannelRef.current = dc;

    dc.onopen = () => {
      setConnectionStatus(ConnectionStatus.Connected);
      startLocalRecording();
      startTimer();
    };
    dc.onclose = () => {
      setConnectionStatus(ConnectionStatus.Closed);
      cleanup();
    };
    dc.onerror = () => {
      setConnectionStatus(ConnectionStatus.Failed);
      cleanup();
    };

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
            addMetadataToTurn(parsed.item_id, {
              sessionId,
              speaker: MessageSender.USER,
              text: parsed.transcript,
            });
            break;

          case 'response.audio_transcript.delta':
            appendDeltaToLastMessage(MessageSender.ASSISTANT, parsed.delta);
            break;

          case 'response.audio_transcript.done':
            addMetadataToTurn(parsed.response_id, {
              sessionId,
              speaker: MessageSender.ASSISTANT,
              text: parsed.transcript,
            });
            break;

          case 'input_audio_buffer.speech_started':
            inputAudioBufferSpeechStartedOffsetMsRef.current = parsed.audio_start_ms;
            addStartOffsetMsToTurn(parsed.item_id, parsed.audio_start_ms);
            if (remoteResponseIdRef.current) {
              addAudioToTurn(remoteResponseIdRef.current, await stopRemoteRecording());
              addEndOffsetMsToTurn(remoteResponseIdRef.current, parsed.audio_start_ms);
              remoteResponseIdRef.current = null;
            }
            break;

          case 'input_audio_buffer.speech_stopped':
            addAudioToTurn(
              parsed.item_id,
              await extractSegment(
                inputAudioBufferSpeechStartedOffsetMsRef.current,
                parsed.audio_end_ms,
                elapsedTimeMsRef.current
              )
            );
            addEndOffsetMsToTurn(parsed.item_id, parsed.audio_end_ms);
            startGetLiveFeedbackInterval();
            break;

          case 'response.content_part.added':
            if (parsed.part.type === 'audio') {
              startRemoteRecording(remoteAudioRef.current?.srcObject as MediaStream);
              addStartOffsetMsToTurn(parsed.response_id, elapsedTimeMsRef.current);
              remoteResponseIdRef.current = parsed.response_id;
            }
            break;

          case 'output_audio_buffer.stopped':
            remoteResponseIdRef.current = null;
            addAudioToTurn(parsed.response_id, await stopRemoteRecording());
            addEndOffsetMsToTurn(parsed.response_id, elapsedTimeMsRef.current);
            break;

          default:
            break;
        }
      } catch {
        // Not JSON – ignore
      }
    };

    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);

    try {
      const sdpText = await sessionService.getSdpResponseTextFromRealtimeApi(
        api,
        sessionId,
        offer.sdp
      );
      await pc.setRemoteDescription({ type: 'answer', sdp: sdpText });
    } catch (err) {
      showErrorToast(err, t('sessionConnectToAIError'));
    }
  }, [
    sessionId,
    startStream,
    addPlaceholderMessage,
    appendDeltaToLastMessage,
    elapsedTimeMsRef,
    startTimer,
    extractSegment,
    startLocalRecording,
    startRemoteRecording,
    stopRemoteRecording,
    addAudioToTurn,
    addMetadataToTurn,
    addStartOffsetMsToTurn,
    localStreamRef,
    addEndOffsetMsToTurn,
    cleanup,
    startGetLiveFeedbackInterval,
    t,
  ]);

  return {
    isMicActive,
    toggleMic,
    connectionStatus,
    initWebRTC,
    remoteAudioRef,
    messages,
    elapsedTimeS,
    cleanup,
    sessionLiveFeedbacks,
  };
}
