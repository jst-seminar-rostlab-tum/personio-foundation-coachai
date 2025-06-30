'use client';

import { Textarea } from '@/components/ui/Textarea';
import { useTranslations } from 'next-intl';
import Input from '@/components/ui/Input';

interface SituationStepProps {
  otherParty: string;
  context: string;
  goal: string;
  onPartyChange: (otherParty: string) => void;
  onContextChange: (context: string) => void;
  onGoalChange: (goal: string) => void;
  isCustom: boolean;
  onCustomCategoryInput: (category: string) => void;
  customCategory: string;
}

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
        className="w-full mb-8"
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
