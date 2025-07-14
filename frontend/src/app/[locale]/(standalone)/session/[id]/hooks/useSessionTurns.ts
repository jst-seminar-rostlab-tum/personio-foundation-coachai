import { CreateSessionTurnRequest } from '@/interfaces/models/Session';
import { sessionService } from '@/services/SessionService';
import { useRef, useCallback } from 'react';
import { api } from '@/services/ApiClient';
import { showErrorToast } from '@/lib/utils/toast';
import { useTranslations } from 'next-intl';

type PartialSessionTurn = Partial<CreateSessionTurnRequest>;

export function useSessionTurns() {
  const t = useTranslations('Session');
  const sessionTurnsMap = useRef<Map<string, PartialSessionTurn>>(new Map());

  const convertSessionTurnToFormData = useCallback((turn: CreateSessionTurnRequest): FormData => {
    const formData = new FormData();
    formData.append('session_id', turn.sessionId);
    formData.append('speaker', turn.speaker);
    formData.append('text', turn.text);
    formData.append('start_offset_ms', String(turn.startOffsetMs));
    formData.append('end_offset_ms', String(turn.endOffsetMs));
    formData.append('audio_file', turn.audioFile);
    return formData;
  }, []);

  const isTurnComplete = useCallback((turnId: string) => {
    const turn = sessionTurnsMap.current.get(turnId);
    if (!turn) return false;
    return !!(
      turn.audioFile &&
      turn.speaker &&
      turn.text &&
      turn.startOffsetMs !== undefined &&
      turn.endOffsetMs !== undefined &&
      turn.sessionId
    );
  }, []);

  const removeTurn = useCallback((turnId: string) => {
    sessionTurnsMap.current.delete(turnId);
  }, []);

  const postSessionTurn = useCallback(
    async (turnId: string) => {
      if (!isTurnComplete(turnId)) return;

      const turn = sessionTurnsMap.current.get(turnId) as CreateSessionTurnRequest;

      try {
        const formData = convertSessionTurnToFormData(turn);
        await sessionService.createSessionTurn(api, formData);
        removeTurn(turnId);
      } catch (error) {
        showErrorToast(error, t('sessionTurnError'));
      }
    },
    [isTurnComplete, convertSessionTurnToFormData, removeTurn, t]
  );

  const addAudioToTurn = useCallback(
    (turnId: string, audioFile: Blob) => {
      const existing = sessionTurnsMap.current.get(turnId) || {};
      sessionTurnsMap.current.set(turnId, {
        ...existing,
        audioFile,
      });

      postSessionTurn(turnId);
    },
    [postSessionTurn]
  );

  const addMetadataToTurn = useCallback(
    (
      turnId: string,
      metadata: Omit<CreateSessionTurnRequest, 'audioFile' | 'startOffsetMs' | 'endOffsetMs'>
    ) => {
      const existing = sessionTurnsMap.current.get(turnId) || {};
      sessionTurnsMap.current.set(turnId, {
        ...existing,
        ...metadata,
      });

      postSessionTurn(turnId);
    },
    [postSessionTurn]
  );

  const addStartOffsetMsToTurn = useCallback((turnId: string, startOffsetMs: number) => {
    const existing = sessionTurnsMap.current.get(turnId) || {};
    sessionTurnsMap.current.set(turnId, {
      ...existing,
      startOffsetMs,
    });
  }, []);

  const addEndOffsetMsToTurn = useCallback(
    (turnId: string, endOffsetMs: number) => {
      const existing = sessionTurnsMap.current.get(turnId) || {};
      sessionTurnsMap.current.set(turnId, {
        ...existing,
        endOffsetMs,
      });

      postSessionTurn(turnId);
    },
    [postSessionTurn]
  );

  return {
    addAudioToTurn,
    addMetadataToTurn,
    addStartOffsetMsToTurn,
    addEndOffsetMsToTurn,
  };
}
