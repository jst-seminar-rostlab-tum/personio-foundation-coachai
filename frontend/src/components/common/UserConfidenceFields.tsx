'use client';

import { UserConfidenceField } from '@/interfaces/models/UserInputFields';
import Slider from '@/components/ui/Slider';
import { cn } from '@/lib/utils/cnMerge';
import { useTranslations } from 'next-intl';

interface UserConfidenceFieldProps {
  className?: string;
  difficulty: number[];
  conflict: number[];
  conversation: number[];
  setDifficulty: (value: number[]) => void;
  setConflict: (value: number[]) => void;
  setConversation: (value: number[]) => void;
}

export default function UserConfidenceFields({
  className,
  difficulty,
  conflict,
  conversation,
  setDifficulty,
  setConflict,
  setConversation,
}: UserConfidenceFieldProps) {
  const t = useTranslations('PersonalizationOptions');
  const confidenceFields: UserConfidenceField[] = [
    {
      title: t('confidenceAreas.givingDifficultFeedback'),
      minLabel: t('confidenceAreas.labels.min'),
      maxLabel: t('confidenceAreas.labels.max'),
      minValue: 0,
      maxValue: 100,
      value: difficulty,
      onChange: setDifficulty,
    },
    {
      title: t('confidenceAreas.managingTeamConflicts'),
      minLabel: t('confidenceAreas.labels.min'),
      maxLabel: t('confidenceAreas.labels.max'),
      minValue: 0,
      maxValue: 100,
      value: conflict,
      onChange: setConflict,
    },
    {
      title: t('confidenceAreas.leadingChallengingConversations'),
      minLabel: t('confidenceAreas.labels.min'),
      maxLabel: t('confidenceAreas.labels.max'),
      minValue: 0,
      maxValue: 100,
      value: conversation,
      onChange: setConversation,
    },
  ];
  return (
    <div className={cn('flex flex-col gap-4 w-full h-63', className)}>
      {confidenceFields.map((field) => (
        <div key={field.title} className="flex flex-col gap-2">
          <span className="text-lg">{field.title}</span>
          <Slider
            className="w-full"
            min={field.minValue}
            max={field.maxValue}
            step={1}
            defaultValue={[50]}
            value={field.value || [50]}
            onValueChange={(value) => {
              if (field.onChange) {
                field.onChange(value);
              }
            }}
          />
          <div className="flex justify-between text-base text-bw-40">
            <span>{field.minLabel}</span>
            <span>{field.maxLabel}</span>
          </div>
        </div>
      ))}
    </div>
  );
}
