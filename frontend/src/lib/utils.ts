/* eslint-disable import/prefer-default-export */
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { UserOption } from '@/interfaces/models/UserInputFields';
import { useTranslations } from 'next-intl';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

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

export function PrimaryGoals(): UserOption[] {
  const tOptions = useTranslations('PersonalizationOptions');

  return [
    {
      id: 'giving_constructive_feedback',
      label: tOptions('leadershipSkillFocus.givingConstructiveFeedback'),
    },
    {
      id: 'managing_team_conflicts',
      label: tOptions('leadershipSkillFocus.managingTeamConflicts'),
    },
    { id: 'performance_reviews', label: tOptions('leadershipSkillFocus.performanceReviews') },
    {
      id: 'motivating_team_members',
      label: tOptions('leadershipSkillFocus.motivatingTeamMembers'),
    },
    {
      id: 'leading_difficult_conversations',
      label: tOptions('leadershipSkillFocus.leadingDifficultConversations'),
    },
    {
      id: 'communicating_organizational_change',
      label: tOptions('leadershipSkillFocus.communicatingOrganizationalChange'),
    },
    {
      id: 'develop_emotional_intelligence',
      label: tOptions('leadershipSkillFocus.developEmotionalIntelligence'),
    },
    {
      id: 'building_inclusive_teams',
      label: tOptions('leadershipSkillFocus.buildingInclusiveTeams'),
    },
    { id: 'negotiation_skills', label: tOptions('leadershipSkillFocus.negotiationSkills') },
    { id: 'coaching_mentoring', label: tOptions('leadershipSkillFocus.coachingMentoring') },
  ];
}

export const formattedDate = (date: string | undefined, locale: string) => {
  if (!date) return '';

  return new Date(date).toLocaleDateString(locale, {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  });
};

export const convertTimeToMinutes = (seconds: number) => {
  return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')}`;
};
