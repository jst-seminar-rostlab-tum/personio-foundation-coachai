'use client';

import { Button } from '@/components/ui/Button';
import { useTranslations } from 'next-intl';
import Image from 'next/image';
import { useState, useEffect } from 'react';

interface ConversationScenarioSuggestionProps {
  suggestion: string;
}

export default function ConversationScenarioSuggestion({
  suggestion,
}: ConversationScenarioSuggestionProps) {
  const t = useTranslations('Dashboard.suggestion');
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Trigger float in animation after component mounts
    const timer = setTimeout(() => {
      setIsVisible(true);
    }, 100); // Small delay to ensure smooth animation

    return () => clearTimeout(timer);
  }, []);

  return (
    <section className="flex flex-col items-center justify-center w-full">
      <div className="flex flex-col md:flex-row md:items-center gap-6 mb-4 justify-center w-full max-w-2xl">
        <div
          className={`relative p-8 max-w-lg break-words border rounded-lg border-bw-10 bg-bw-10 mx-auto transition-all duration-1000 ease-out ${
            isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
          }`}
        >
          <span className="block whitespace-pre-line leading-loose text-base">{suggestion}</span>
          <Button className="mt-4">{t('startButton')}</Button>
          <span className="hidden md:block absolute right-[-20px] top-1/2 -translate-y-1/2 w-0 h-0 border-y-[20px] border-y-transparent border-l-[20px] border-l-bw-10"></span>
          <span className="block md:hidden absolute left-1/2 bottom-[-20px] -translate-x-1/2 w-0 h-0 border-x-[20px] border-x-transparent border-t-[20px] border-t-bw-10"></span>
        </div>
        <Image
          src="/images/mascot.png"
          alt="Mascot"
          width={144}
          height={120}
          className={`object-contain mx-auto transition-all duration-1000 ease-out ${
            isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
          }`}
        />
      </div>
    </section>
  );
}
