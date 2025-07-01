import { CreateSessionTurnRequest } from '@/interfaces/models/Session';
import { sessionService } from '@/services/SessionService';
import { useRef, useState } from 'react';
import { api } from '@/services/ApiClient';
import { showErrorToast } from '@/lib/toast';

type PartialSessionTurn = Partial<CreateSessionTurnRequest>;

export function useSessionTurns() {
  const sessionTurnsMap = useRef<Map<string, PartialSessionTurn>>(new Map());
  const [audioUrls, setAudioUrls] = useState<{ url: string; filename: string }[]>([]);

  const addAudioToTurn = (turnId: string, audioFile: Blob) => {
    const existing = sessionTurnsMap.current.get(turnId) || {};
    sessionTurnsMap.current.set(turnId, {
      ...existing,
      audioFile,
    });

    const url = URL.createObjectURL(audioFile);
    setAudioUrls((prev) => [...prev, { url, filename: turnId }]);

    postSessionTurn(turnId);
  };

  const addMetadataToTurn = (
    turnId: string,
    metadata: Omit<CreateSessionTurnRequest, 'audioFile' | 'startOffsetMs'>
  ) => {
    const existing = sessionTurnsMap.current.get(turnId) || {};
    sessionTurnsMap.current.set(turnId, {
      ...existing,
      ...metadata,
    });

    postSessionTurn(turnId);
  };

  const addStartOffsetMsToTurn = (turnId: string, startOffsetMs: number) => {
    const existing = sessionTurnsMap.current.get(turnId) || {};
    sessionTurnsMap.current.set(turnId, {
      ...existing,
      startOffsetMs,
    });
  };

  const isTurnComplete = (turnId: string) => {
    const turn = sessionTurnsMap.current.get(turnId);
    if (!turn) return false;
    return !!(
      turn.audioFile &&
      turn.speaker &&
      turn.text &&
      turn.startOffsetMs !== undefined &&
      turn.sessionId
    );
  };

  const removeTurn = (turnId: string) => {
    sessionTurnsMap.current.delete(turnId);
  };

  function sessionTurnToFormData(turn: CreateSessionTurnRequest): FormData {
    const formData = new FormData();
    formData.append('session_id', turn.sessionId);
    formData.append('speaker', turn.speaker);
    formData.append('text', turn.text);
    formData.append('start_offset_ms', String(turn.startOffsetMs));
    formData.append('audio_file', turn.audioFile);
    return formData;
  }

  const postSessionTurn = async (turnId: string) => {
    if (!isTurnComplete(turnId)) return;

    const turn = sessionTurnsMap.current.get(turnId) as CreateSessionTurnRequest;

    try {
      const formData = sessionTurnToFormData(turn);
      await sessionService.createSessionTurn(api, formData);
      removeTurn(turnId);
    } catch (error) {
      showErrorToast(error, 'Failed to post session turn');
    }
  };

  return {
    addAudioToTurn,
    addMetadataToTurn,
    addStartOffsetMsToTurn,
    audioUrls,
  };
}
