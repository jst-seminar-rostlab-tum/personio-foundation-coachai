'use client';

import { Textarea } from '@/components/ui/Textarea';
import { useTranslations } from 'next-intl';
import { SituationStepProps } from '@/interfaces/SituationStepProps';
import Input from '@/components/ui/Input';

export function SituationStep({
  otherParty,
  context,
  goal,
  onPartyChange,
  onContextChange,
  onGoalChange,
  onCustomCategoryInput,
  customCategory,
  isCustom,
}: SituationStepProps) {
  const t = useTranslations('ConversationScenario');
  return (
    <div>
      <div className="text-xl text-font-dark text-center w-full mb-8">{t('situation.title')}</div>
      {isCustom && (
        <>
          <div className="text-lg text-font-dark mb-4">{t('category.customInput')}</div>
          <Textarea
            className="w-full mb-8"
            value={customCategory}
            placeholder={t('category.customPlaceholder')}
            onChange={(e) => onCustomCategoryInput(e.target.value)}
          />
        </>
      )}

      <div className="text-lg text-font-dark mb-4">{t('situation.otherParty.title')}</div>
      <Input
        className="border-input placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-ring/50 dark:bg-input/30 w-full rounded-md border bg-transparent px-3 py-2 text-base shadow-xs transition-[color,box-shadow] outline-none focus-visible:ring-[3px] disabled:cursor-not-allowed disabled:opacity-50 md:text-sm mb-8"
        value={otherParty}
        placeholder={t('situation.otherParty.placeholder')}
        onChange={(e) => onPartyChange(e.target.value)}
      />

      <div className="text-lg text-font-dark mb-4">{t('situation.context.title')}</div>
      <Textarea
        placeholder={t('situation.context.placeholder')}
        className="min-h-[96px] mb-8"
        value={context}
        onChange={(e) => onContextChange(e.target.value)}
      />
      <div className="text-lg text-font-dark mb-4">{t('situation.goal.title')}</div>
      <Textarea
        placeholder={t('situation.goal.placeholder')}
        className="min-h-[96px] mb-8"
        value={goal}
        onChange={(e) => onGoalChange(e.target.value)}
      />
    </div>
  );
}
