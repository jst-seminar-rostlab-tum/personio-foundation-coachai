'use client';

import Label from '@/components/ui/Label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/RadioGroup';
import Input from '@/components/ui/Input';
import { Textarea } from '@/components/ui/Textarea';
import { useTranslations } from 'next-intl';
import { SituationStepProps } from '@/interfaces/SituationStepProps';

export function SituationStep({
  party,
  context,
  goal,
  onPartyChange,
  onContextChange,
  onGoalChange,
  onCustomCategoryInput,
  customCategory,
  isCustom,
}: SituationStepProps) {
  const t = useTranslations('NewTraining');
  return (
    <div>
      <div className="text-xl text-font-dark text-center w-full mb-8">{t('situation.title')}</div>
      {isCustom && (
        <>
          <div className="text-lg text-font-dark mb-4">{t('category.customInput')}</div>
          <Input
            className="w-full mb-8"
            value={customCategory}
            placeholder={t('category.customPlaceholder')}
            onChange={(e) => onCustomCategoryInput(e.target.value)}
          />
        </>
      )}

      <div className="text-lg text-font-dark mb-4">{t('situation.party.title')}</div>
      <RadioGroup
        value={party.type}
        onValueChange={(value) => onPartyChange(value)}
        className="mb-8"
      >
        <div className="flex items-center space-x-2">
          <RadioGroupItem value="employee" id="r1" />
          <Label htmlFor="r1">{t('situation.party.options.employee')}</Label>
        </div>
        <div className="flex items-center space-x-2">
          <RadioGroupItem value="manager" id="r2" />
          <Label htmlFor="r2">{t('situation.party.options.manager')}</Label>
        </div>
        <div className="flex items-center space-x-2">
          <RadioGroupItem value="peer" id="r3" />
          <Label htmlFor="r3">{t('situation.party.options.peer')}</Label>
        </div>
        <div className="flex items-center space-x-2">
          <RadioGroupItem value="stakeholder" id="r4" />
          <Label htmlFor="r4">{t('situation.party.options.stakeholder')}</Label>
        </div>
        <div className="flex items-center space-x-2">
          <RadioGroupItem value="other" id="r5" />
          <Input
            placeholder={t('situation.party.otherPlaceholder')}
            value={party.otherName}
            onChange={(e) => onPartyChange('other', e.target.value)}
            disabled={party.type !== 'other'}
          />
        </div>
      </RadioGroup>

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
