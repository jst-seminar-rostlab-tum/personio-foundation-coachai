import { CreateSessionTurnRequest } from '@/interfaces/models/Session';
import { sessionService } from '@/services/SessionService';
import { useRef, useCallback } from 'react';
import { api } from '@/services/ApiClient';
import { showErrorToast } from '@/lib/utils/toast';
import { useTranslations } from 'next-intl';

/**
 * Partial session turn data collected before upload.
 */
type PartialSessionTurn = Partial<CreateSessionTurnRequest>;

/**
 * Buffers and uploads session turns once all parts are available.
 */
export function useSessionTurns() {
  const t = useTranslations('Session');
  const sessionTurnsMap = useRef<Map<string, PartialSessionTurn>>(new Map());

  /**
   * Builds a multipart form payload for a session turn.
   */
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

  /**
   * Checks if a turn has all required fields to upload.
   */
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

  /**
   * Removes a buffered turn after upload.
   */
  const removeTurn = useCallback((turnId: string) => {
    sessionTurnsMap.current.delete(turnId);
  }, []);

  /**
   * Uploads a buffered turn if it is complete.
   */
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

  /**
   * Attaches audio to a turn and attempts upload.
   */
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

  /**
   * Attaches metadata to a turn and attempts upload.
   */
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

  /**
   * Sets the start offset for a turn.
   */
  const addStartOffsetMsToTurn = useCallback((turnId: string, startOffsetMs: number) => {
    const existing = sessionTurnsMap.current.get(turnId) || {};
    sessionTurnsMap.current.set(turnId, {
      ...existing,
      startOffsetMs,
    });
  }, []);

  /**
   * Sets the end offset and attempts upload.
   */
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
