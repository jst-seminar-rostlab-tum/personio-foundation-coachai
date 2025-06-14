/* eslint-disable import/prefer-default-export */
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { UserOption } from '@/interfaces/UserInputFields';
import { useTranslations } from 'next-intl';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function UserRoles(): UserOption[] {
  const tOptions = useTranslations('PersonalizationOptions');
  return [
    {
      id: 'hr_professional',
      label: tOptions('experience_roles.hr_professional.label'),
      labelHint: tOptions('experience_roles.hr_professional.description'),
    },
    {
      id: 'team_leader',
      label: tOptions('experience_roles.team_leader.label'),
      labelHint: tOptions('experience_roles.team_leader.description'),
    },
    {
      id: 'executive',
      label: tOptions('experience_roles.executive.label'),
      labelHint: tOptions('experience_roles.executive.description'),
    },
    {
      id: 'other',
      label: tOptions('experience_roles.other.label'),
      labelHint: tOptions('experience_roles.other.description'),
    },
  ];
}

export function PrimaryGoals(): UserOption[] {
  const tOptions = useTranslations('PersonalizationOptions');

  return [
    {
      id: 'giving_constructive_feedback',
      label: tOptions('leadership_skill_focus.giving_constructive_feedback'),
    },
    {
      id: 'managing_team_conflicts',
      label: tOptions('leadership_skill_focus.managing_team_conflicts'),
    },
    { id: 'performance_reviews', label: tOptions('leadership_skill_focus.performance_reviews') },
    {
      id: 'motivating_team_members',
      label: tOptions('leadership_skill_focus.motivating_team_members'),
    },
    {
      id: 'leading_difficult_conversations',
      label: tOptions('leadership_skill_focus.leading_difficult_conversations'),
    },
    {
      id: 'communicating_organizational_change',
      label: tOptions('leadership_skill_focus.communicating_organizational_change'),
    },
    {
      id: 'develop_emotional_intelligence',
      label: tOptions('leadership_skill_focus.develop_emotional_intelligence'),
    },
    {
      id: 'building_inclusive_teams',
      label: tOptions('leadership_skill_focus.building_inclusive_teams'),
    },
    { id: 'negotiation_skills', label: tOptions('leadership_skill_focus.negotiation_skills') },
    { id: 'coaching_mentoring', label: tOptions('leadership_skill_focus.coaching_mentoring') },
  ];
}
