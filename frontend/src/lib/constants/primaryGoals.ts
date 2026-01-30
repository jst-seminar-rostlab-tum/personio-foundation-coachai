import { UserOption } from '@/interfaces/models/UserInputFields';
import { useTranslations } from 'next-intl';

/**
 * Returns localized primary goal options for user preferences.
 */
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
