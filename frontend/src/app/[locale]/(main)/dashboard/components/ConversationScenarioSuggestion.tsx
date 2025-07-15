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
    <section className="flex flex-col items-center justify-center w-full">
      <div className="flex flex-col sm:flex-row sm:items-center gap-6 justify-center w-full max-w-2xl">
        {/* Bubble first on mobile, mascot below; side by side on sm+ */}
        <div className="relative p-8 max-w-lg break-words border rounded-lg border-bw-10 bg-bw-10 mx-auto">
          <span className="block whitespace-pre-line leading-loose text-base">{suggestion}</span>
          <Button className="mt-4">{t('startButton')}</Button>
          {/* Triangle pointer: right on sm+, bottom on mobile */}
          <span className="hidden sm:block absolute right-[-20px] top-1/2 -translate-y-1/2 w-0 h-0 border-y-[20px] border-y-transparent border-l-[20px] border-l-bw-10"></span>
          <span className="block sm:hidden absolute left-1/2 bottom-[-20px] -translate-x-1/2 w-0 h-0 border-x-[20px] border-x-transparent border-t-[20px] border-t-bw-10"></span>
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
