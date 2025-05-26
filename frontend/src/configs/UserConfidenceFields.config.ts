import { UserConfidenceField } from '@/interfaces/UserInputFields';
import { useTranslations } from 'next-intl';

export function useUserConfidenceFields(): UserConfidenceField[] {
  const t = useTranslations('confidenceFields');
  return [
    {
      title: t('givingFeedback.title'),
      minLabel: t('minLabel'),
      maxLabel: t('maxLabel'),
      minValue: 0,
      maxValue: 100,
    },
    {
      title: t('teamConflicts.title'),
      minLabel: t('minLabel'),
      maxLabel: t('maxLabel'),
      minValue: 0,
      maxValue: 100,
    },
    {
      title: t('challengingConversations.title'),
      minLabel: t('minLabel'),
      maxLabel: t('maxLabel'),
      minValue: 0,
      maxValue: 100,
    },
  ];
}
