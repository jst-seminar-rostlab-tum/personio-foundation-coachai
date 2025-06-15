'use client';

import { useState } from 'react';
import { ChevronUp } from 'lucide-react';

export default function SimulationRealtimeSuggestions() {
  const [showSuggestions, setShowSuggestions] = useState(false);
  const suggestions = [
    {
      title: 'Positive Tone',
      message: 'Your tone is calm. Keep it up',
    },
    {
      title: 'Mind What You Say',
      message:
        'Responding with "Oops" after being confronted with an accusation is not professional.',
    },
    {
      title: 'Try Asking',
      message: '"What specific challenges are you facing with these deadlines?"',
    },
    {
      title: 'Potential Next Steps',
      message:
        'You could try asking: "What specific challenges are you facing with these deadlines?"',
    },
  ];

  return (
    <>
      <div
        className={`flex items-center justify-start gap-2 px-4 md:px-6 py-4 bg-white border-y border-bw-10 hover:cursor-pointer group relative z-20`}
        onClick={() => setShowSuggestions((prev) => !prev)}
      >
        <ChevronUp
          className={`w-5 h-5 transition-transform duration-600 ${showSuggestions ? 'rotate-180' : ''}`}
        />
        <span className="font-medium text-font-dark text-sm group-hover:underline">
          Real-time Suggestions
        </span>
      </div>
      <div
        className={`w-full overflow-hidden transition-all duration-600 ease-in-out ${
          showSuggestions ? 'max-h-[45%]' : 'max-h-0'
        }`}
      >
        <div className="w-full flex flex-col overflow-y-auto [&::-webkit-scrollbar]:hidden [-ms-overflow-style:'none'] [scrollbar-width:'none'] p-6 border-b border-background-light">
          <ul className="flex flex-col gap-4 w-full">
            {suggestions.map((suggestion, idx) => (
              <li key={idx} className="bg-background-light rounded-lg border border-bw-20 p-4">
                <div className="font-semibold text-font-dark mb-1">{suggestion.title}</div>
                <div className="text-sm text-font-dark leading-snug">{suggestion.message}</div>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </>
  );
}
