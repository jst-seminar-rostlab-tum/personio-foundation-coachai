import { useEffect, useRef, useState } from 'react';

export function useElapsedTime() {
  const [elapsedTimeS, setElapsedTimeS] = useState(0);
  const elapsedTimeMsRef = useRef(0);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const startTimestampRef = useRef<number | null>(null);

  const startTimer = () => {
    if (intervalRef.current) return;

    startTimestampRef.current = performance.now();
    intervalRef.current = setInterval(() => {
      if (startTimestampRef.current === null) return;

      const now = performance.now();
      const elapsedMs = now - startTimestampRef.current;

      elapsedTimeMsRef.current = Math.floor(elapsedMs);
      setElapsedTimeS(Math.floor(elapsedMs / 1000));
    }, 100);
  };

  const stopTimer = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    startTimestampRef.current = null;
  };

  useEffect(() => {
    return () => stopTimer();
  }, []);

  return {
    elapsedTimeS,
    elapsedTimeMsRef,
    startTimer,
    stopTimer,
  };
}
