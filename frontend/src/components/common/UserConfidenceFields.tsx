'use client';

import { UserConfidenceField } from '@/interfaces/UserInputFields';
import Slider from '@/components/ui/Slider';
import { cn } from '@/lib/utils';
import { useTranslations } from 'next-intl';

const UserConfidenceFields: React.FC<{ className?: string }> = ({ className }) => {
  const t = useTranslations('PersonalizationOptions');
  const confidenceFields: UserConfidenceField[] = [
    {
      title: t('confidence_areas.difficult'),
      minLabel: t('confidence_areas.labels.min'),
      maxLabel: t('confidence_areas.labels.max'),
      minValue: 0,
      maxValue: 100,
    },
    {
      title: t('confidence_areas.conflicts'),
      minLabel: t('confidence_areas.labels.min'),
      maxLabel: t('confidence_areas.labels.max'),
      minValue: 0,
      maxValue: 100,
    },
    {
      title: t('confidence_areas.conversations'),
      minLabel: t('confidence_areas.labels.min'),
      maxLabel: t('confidence_areas.labels.max'),
      minValue: 0,
      maxValue: 100,
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
};

export default UserConfidenceFields;
