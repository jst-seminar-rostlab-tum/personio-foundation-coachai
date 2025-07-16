'use client';

import { Button } from '@/components/ui/Button';
import { ConversationScenario } from '@/interfaces/models/ConversationScenario';
import { showErrorToast } from '@/lib/utils/toast';
import { api } from '@/services/ApiClient';
import { conversationScenarioService } from '@/services/ConversationScenarioService';
import { useTranslations } from 'next-intl';
import Image from 'next/image';
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
  const router = useRouter();

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
      showErrorToast(err, 'Failed to create suggested scenario');
    }
  };

  return (
    <section className="flex flex-col items-center justify-center w-full">
      <div className="flex flex-col md:flex-row md:items-center gap-6 mb-4 justify-center w-full max-w-2xl">
        <div className="relative p-8 max-w-lg break-words border rounded-lg border-bw-10 bg-bw-10 mx-auto">
          <span className="block whitespace-pre-line leading-loose text-base">{suggestion}</span>
          <Button className="mt-4" onClick={onClickStartSuggestedScenario}>
            {t('startButton')}
          </Button>
          <span className="hidden md:block absolute right-[-20px] top-1/2 -translate-y-1/2 w-0 h-0 border-y-[20px] border-y-transparent border-l-[20px] border-l-bw-10"></span>
          <span className="block md:hidden absolute left-1/2 bottom-[-20px] -translate-x-1/2 w-0 h-0 border-x-[20px] border-x-transparent border-t-[20px] border-t-bw-10"></span>
        </div>
        <Image
          src="/images/mascot.png"
          alt="Mascot"
          width={144}
          height={120}
          className="object-contain mx-auto"
        />
      </div>
    </section>
  );
}
