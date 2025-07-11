import { Button } from '@/components/ui/Button';
import { getTranslations } from 'next-intl/server';
import Image from 'next/image';

interface ConversationScenarioSuggestionProps {
  suggestion: string;
}

export default async function ConversationScenarioSuggestion({
  suggestion,
}: ConversationScenarioSuggestionProps) {
  const t = await getTranslations('Dashboard.suggestion');

  return (
    <section className="flex flex-col md:flex-row md:items-center md:justify-start gap-4">
      <div className="flex items-center gap-4">
        <Image src="/images/owl.svg" alt="Owl" width={100} height={100} />
        <div className="relative p-4 max-w-lg break-words border rounded-lg border-bw-10 bg-bw-10">
          <span className="block whitespace-pre-line text-lg">{suggestion}</span>
          <Button variant={'secondary'} className="mt-4">
            {t('startButton')}
          </Button>
          <span className="absolute left-[-16px] top-1/2 -translate-y-1/2 w-0 h-0 border-t-8 border-b-8 border-t-transparent border-b-transparent border-r-[16px] border-r-bw-10"></span>
          <span className="absolute left-[-18px] top-1/2 -translate-y-1/2 w-0 h-0 border-t-8 border-b-8 border-t-transparent border-b-transparent border-r-[16px] border-r-bw-10 z-[-1]"></span>
        </div>
      </div>
    </section>
  );
}
