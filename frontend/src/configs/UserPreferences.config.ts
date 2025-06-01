import { UserPreference } from '@/interfaces/UserInputFields';
import { useTranslations } from 'next-intl';

export function useUserPreferences(): UserPreference[] {
  const t = useTranslations('TrainingSettings.preferences');
  return [
    {
      label: t('language.label'),
      options: [
        { code: 'en', name: t('language.en') },
        { code: 'es', name: t('language.es') },
        { code: 'fr', name: t('language.fr') },
      ],
      defaultValue: 'en',
    },
    {
      label: t('learningStyle.label'),
      options: [
        { code: 'visual', name: t('learningStyle.visual') },
        { code: 'handson', name: t('learningStyle.handson') },
        { code: 'auditory', name: t('learningStyle.auditory') },
        { code: 'kinesthetic', name: t('learningStyle.kinesthetic') },
      ],
      defaultValue: 'handson',
    },
    {
      label: t('session.label'),
      options: [
        { code: 'short', name: t('session.short') },
        { code: 'medium', name: t('session.medium') },
        { code: 'long', name: t('session.long') },
      ],
      defaultValue: 'medium',
    },
  ];
}
