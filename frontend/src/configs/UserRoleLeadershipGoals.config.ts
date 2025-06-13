import { UserPreference } from '@/interfaces/UserInputFields';
import { PrimaryGoals, UserRoles } from '@/lib/utils';
import { useTranslations } from 'next-intl';

export function useUserRoleLeadershipGoals(): UserPreference[] {
  const t = useTranslations('TrainingSettings.leadershipGoals');
  return [
    {
      label: t('currentRole.label'),
      options: UserRoles(),
      defaultValue: 'team_leader',
    },
    {
      label: t('primaryGoals.label'),
      options: PrimaryGoals(),
      defaultValue: 'managing_team_conflicts',
    },
  ];
}
