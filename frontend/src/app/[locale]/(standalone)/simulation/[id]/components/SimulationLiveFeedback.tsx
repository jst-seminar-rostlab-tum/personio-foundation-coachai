'use client';

import { useState } from 'react';
import { ChevronUp } from 'lucide-react';
import { SessionLiveFeedback } from '@/interfaces/models/SessionLiveFeedback';
import { useTranslations } from 'next-intl';

interface SimulationLiveFeedbackProps {
  liveFeedbacks: SessionLiveFeedback[];
}

export default function SimulationLiveFeedback({ liveFeedbacks }: SimulationLiveFeedbackProps) {
  const t = useTranslations('Simulation.LiveFeedback');
  const [showSuggestions, setShowSuggestions] = useState(false);

  return (
    <>
      <div
        className={`flex items-center justify-start gap-2 py-4 bg-white border-y border-bw-10 hover:cursor-pointer group relative z-20`}
        onClick={() => setShowSuggestions((prev) => !prev)}
      >
        <div className="w-full max-w-7xl mx-auto flex items-center gap-2 px-[clamp(1.25rem,4vw,4rem)]">
          <ChevronUp
            className={`w-5 h-5 transition-transform duration-600 ${showSuggestions ? 'rotate-180' : ''}`}
          />
          <span className="font-medium text-font-dark text-sm group-hover:underline">
            {t('title')}
          </span>
        </div>
      </div>
      <div
        className={`w-full overflow-hidden transition-all duration-600 ease-in-out ${
          showSuggestions ? 'max-h-[30vh] md:max-h-[25vh]' : 'max-h-0'
        }`}
      >
        <div className="w-full">
          <div
            className="w-full max-w-7xl mx-auto flex flex-col overflow-y-auto 
            [&::-webkit-scrollbar]:hidden 
            [-ms-overflow-style:'none'] 
            [scrollbar-width:'none'] 
            p-6 
            px-[clamp(1.25rem,4vw,4rem)] 
            max-h-[30vh] md:max-h-[25vh]"
          >
            <ul className="flex flex-col gap-4 w-full">
              {liveFeedbacks.map((liveFeedback, idx) => (
                <li key={idx} className="bg-background-light rounded-lg border border-bw-20 p-4">
                  <div className="font-semibold text-font-dark mb-1">{liveFeedback.heading}</div>
                  <div className="text-sm text-font-dark leading-snug">
                    {liveFeedback.feedbackText}
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </>
  );
}
