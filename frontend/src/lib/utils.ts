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
      id: 'hrProfessional',
      label: tOptions('experienceRoles.hrProfessional.label'),
      labelHint: tOptions('experienceRoles.hrProfessional.description'),
    },
    {
      id: 'teamLeader',
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

export function PrimaryGoals(): UserOption[] {
  const tOptions = useTranslations('PersonalizationOptions');

  return [
    {
      id: 'givingConstructiveFeedback',
      label: tOptions('leadershipSkillFocus.givingConstructiveFeedback'),
    },
    {
      id: 'managingTeamConflicts',
      label: tOptions('leadershipSkillFocus.managingTeamConflicts'),
    },
    { id: 'performanceReviews', label: tOptions('leadershipSkillFocus.performanceReviews') },
    {
      id: 'motivatingTeamMembers',
      label: tOptions('leadershipSkillFocus.motivatingTeamMembers'),
    },
    {
      id: 'leadingDifficultConversations',
      label: tOptions('leadershipSkillFocus.leadingDifficultConversations'),
    },
    {
      id: 'communicatingOrganizationalChange',
      label: tOptions('leadershipSkillFocus.communicatingOrganizationalChange'),
    },
    {
      id: 'developEmotionalIntelligence',
      label: tOptions('leadershipSkillFocus.developEmotionalIntelligence'),
    },
    {
      id: 'buildingInclusiveTeams',
      label: tOptions('leadershipSkillFocus.buildingInclusiveTeams'),
    },
    { id: 'negotiationSkills', label: tOptions('leadershipSkillFocus.negotiationSkills') },
    { id: 'coachingMentoring', label: tOptions('leadershipSkillFocus.coachingMentoring') },
  ];
}
