import { useCallback, useRef, useState } from 'react';

/**
 * Tracks elapsed time with start/stop controls.
 */
export function useElapsedTime() {
  const [elapsedTimeS, setElapsedTimeS] = useState(0);
  const elapsedTimeMsRef = useRef(0);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const startTimestampRef = useRef<number | null>(null);

  /**
   * Starts the interval timer for elapsed time updates.
   */
  const startTimer = useCallback(() => {
    if (intervalRef.current) return;

    startTimestampRef.current = performance.now();
    intervalRef.current = setInterval(() => {
      if (startTimestampRef.current === null) return;

      const now = performance.now();
      const elapsedMs = now - startTimestampRef.current;

      elapsedTimeMsRef.current = Math.floor(elapsedMs);
      setElapsedTimeS(Math.floor(elapsedMs / 1000));
    }, 100);
  }, []);

  /**
   * Stops the interval timer and resets the start timestamp.
   */
  const stopTimer = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    startTimestampRef.current = null;
  }, []);

  return {
    elapsedTimeS,
    elapsedTimeMsRef,
    startTimer,
    stopTimer,
  };
}
