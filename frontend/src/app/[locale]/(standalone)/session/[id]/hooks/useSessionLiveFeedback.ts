import { SessionLiveFeedback } from '@/interfaces/models/Session';
import { api } from '@/services/ApiClient';
import { sessionService } from '@/services/SessionService';
import { useCallback, useRef, useState } from 'react';

export function useSessionLiveFeedback(sessionId: string) {
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const isFetchingRef = useRef(false);
  const [sessionLiveFeedbacks, setSessionLiveFeedbacks] = useState<SessionLiveFeedback[]>([]);

  const stopGetLiveFeedbackInterval = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  const startGetLiveFeedbackInterval = useCallback(() => {
    stopGetLiveFeedbackInterval();

    intervalRef.current = setInterval(async () => {
      if (isFetchingRef.current) return;

      isFetchingRef.current = true;
      try {
        const newSessionLiveFeedbacks = await sessionService.getSessionLiveFeedback(api, sessionId);

        setSessionLiveFeedbacks((prev) => {
          if (
            newSessionLiveFeedbacks.length > prev.length ||
            (newSessionLiveFeedbacks.length > 0 &&
              prev.length > 0 &&
              newSessionLiveFeedbacks[0].id !== prev[0].id)
          ) {
            stopGetLiveFeedbackInterval();
            return newSessionLiveFeedbacks;
          }
          return prev;
        });
      } catch {
        // silent catch — retry on next interval
      } finally {
        isFetchingRef.current = false;
      }
    }, 1000);
  }, [sessionId, stopGetLiveFeedbackInterval]);

  return {
    startGetLiveFeedbackInterval,
    stopGetLiveFeedbackInterval,
    sessionLiveFeedbacks,
  };
}
