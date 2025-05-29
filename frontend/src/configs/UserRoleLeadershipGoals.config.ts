import { UserPreference } from '@/interfaces/UserInputFields';
import { useTranslations } from 'next-intl';

export function useUserRoleLeadershipGoals(): UserPreference[] {
  const t = useTranslations('TrainingSettings.leadershipGoals');
  return [
    {
      label: t('currentRole.label'),
      options: [
        { code: 'tl', name: t('currentRole.tl') },
        { code: 'rec', name: t('currentRole.rec') },
        { code: 'tr', name: t('currentRole.tr') },
      ],
      defaultValue: 'tl',
    },
    {
      label: t('primaryGoals.label'),
      options: [
        { code: 'feedback', name: t('primaryGoals.feedback') },
        { code: 'coaching', name: t('primaryGoals.coaching') },
        { code: 'coping', name: t('primaryGoals.coping') },
      ],
      defaultValue: 'coaching',
    },
  ];
}
