'use client';

import { useState, useEffect } from 'react';
import SimulationHeader from './SimulationHeader';
import SimulationFooter from './SimulationFooter';
import SimulationRealtimeSuggestions from './SimulationRealtimeSuggestions';
import SimulationMessages from './SimulationMessages';

export default function SimulationPageComponent() {
  const [time, setTime] = useState(0);
  const [isPaused, setIsPaused] = useState(false);

  useEffect(() => {
    if (!isPaused) {
      const interval = setInterval(() => {
        setTime((prev) => prev + 1);
      }, 1000);
      return () => clearInterval(interval);
    }
    return undefined;
  }, [isPaused]);

  return (
    <div className="flex flex-col h-screen">
      <SimulationHeader time={time} />

      <div className="flex-1 relative p-6 md:p-8  overflow-y-auto [&::-webkit-scrollbar]:hidden [-ms-overflow-style:'none'] [scrollbar-width:'none']">
        <SimulationMessages />
      </div>

      <SimulationRealtimeSuggestions />

      <SimulationFooter isPaused={isPaused} setIsPaused={setIsPaused} />
    </div>
  );
}
