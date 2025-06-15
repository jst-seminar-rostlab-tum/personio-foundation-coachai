'use client';

import { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';

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
        className={`flex items-center justify-start gap-2 px-4 py-4 bg-white border-b border-gray-200 hover:cursor-pointer group relative z-20 ${
          showSuggestions ? 'border-t' : ''
        }`}
        onClick={() => setShowSuggestions((prev) => !prev)}
      >
        {showSuggestions ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
        <span className="font-medium text-font-dark text-sm group-hover:underline">
          Real-time Suggestions
        </span>
      </div>
      {showSuggestions && (
        <div className="w-full max-h-[35vh] flex flex-col overflow-y-auto [&::-webkit-scrollbar]:hidden [-ms-overflow-style:'none'] [scrollbar-width:'none'] p-4 border-b border-background-light">
          <ul className="space-y-3 w-full">
            {suggestions.map((suggestion, idx) => (
              <li
                key={idx}
                className="bg-background-light rounded-lg border border-bw-20 px-4 py-3"
              >
                <div className="font-semibold text-font-dark mb-1">{suggestion.title}</div>
                <div className=" text-sm text-font-dark leading-snug">{suggestion.message}</div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </>
  );
}
