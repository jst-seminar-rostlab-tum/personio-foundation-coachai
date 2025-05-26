import { UserPreference } from '@/interfaces/UserInputFields';
import { useTranslations } from 'next-intl';

export function useUserRoleLeadershipGoals(): UserPreference[] {
  const t = useTranslations('leadershipGoals');
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
      label: t('experience.label'),
      options: [
        { code: 'strong', name: t('experience.strong') },
        { code: 'intermediate', name: t('experience.intermediate') },
        { code: 'beginner', name: t('experience.beginner') },
        { code: 'no', name: t('experience.no') },
      ],
      defaultValue: 'intermediate',
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
