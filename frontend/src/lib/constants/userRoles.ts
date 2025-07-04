import { UserOption } from '@/interfaces/models/UserInputFields';
import { useTranslations } from 'next-intl';

export function UserRoles(): UserOption[] {
  const tOptions = useTranslations('PersonalizationOptions');
  return [
    {
      id: 'hr_professional',
      label: tOptions('experienceRoles.hrProfessional.label'),
      labelHint: tOptions('experienceRoles.hrProfessional.description'),
    },
    {
      id: 'team_leader',
      label: tOptions('experienceRoles.teamLeader.label'),
      labelHint: tOptions('experienceRoles.teamLeader.description'),
    },
    {
      id: 'executive',
      label: tOptions('experienceRoles.executive.label'),
      labelHint: tOptions('experienceRoles.executive.description'),
    },
    {
      id: 'other',
      label: tOptions('experienceRoles.other.label'),
      labelHint: tOptions('experienceRoles.other.description'),
    },
  ];
}
