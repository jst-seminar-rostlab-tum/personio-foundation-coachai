'use client';

import { Button } from '@/components/ui/Button';
import { useTranslations } from 'next-intl';
import Image from 'next/image';
import { useState, useEffect } from 'react';
import { ConversationScenario } from '@/interfaces/models/ConversationScenario';
import { showErrorToast } from '@/lib/utils/toast';
import { api } from '@/services/ApiClient';
import { conversationScenarioService } from '@/services/ConversationScenarioService';
import { useRouter } from 'next/navigation';

interface ConversationScenarioSuggestionProps {
  suggestion: string;
  scenario: ConversationScenario;
}

export default function ConversationScenarioSuggestion({
  suggestion,
  scenario,
}: ConversationScenarioSuggestionProps) {
  const t = useTranslations('Dashboard.suggestion');
  const tConversationScenario = useTranslations('ConversationScenario');
  const router = useRouter();
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(true);
    }, 100);

    return () => clearTimeout(timer);
  }, []);

  if (!suggestion || !scenario) return null;

  const onClickStartSuggestedScenario = async () => {
    try {
      const { data } = await conversationScenarioService.createConversationScenario(
        api,
        scenario,
        true
      );
      router.push(`/preparation/${data.scenarioId}`);
    } catch (err) {
      showErrorToast(err, tConversationScenario('errorMessage'));
    }
  };

  return (
    <section className="flex flex-col items-center justify-center w-full">
      <div className="flex flex-col md:flex-row md:items-center gap-6 mb-4 justify-center w-full max-w-2xl">
        <div
          className={`relative p-8 max-w-lg break-words border rounded-lg border-custom-beige bg-custom-beige mx-auto transition-all duration-1000 ease-out ${
            isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
          }`}
        >
          <span className="block whitespace-pre-line leading-loose text-base">{suggestion}</span>
          <Button className="mt-4" onClick={onClickStartSuggestedScenario}>
            {t('startButton')}
          </Button>
          <span className="hidden md:block absolute right-[-20px] top-1/2 -translate-y-1/2 w-0 h-0 border-y-[20px] border-y-transparent border-l-[20px] border-l-custom-beige"></span>
          <span className="block md:hidden absolute left-1/2 bottom-[-20px] -translate-x-1/2 w-0 h-0 border-x-[20px] border-x-transparent border-t-[20px] border-t-custom-beige"></span>
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
