import { ConversationCategory } from '@/interfaces/models/ConversationScenario';
import { useTranslations } from 'next-intl';

export function Categories(): ConversationCategory[] {
  const t = useTranslations('ConversationScenario.categories');
  return [
    {
      id: 'giving_feedback',
      name: t('givingFeedback.name'),
      iconUri: '/images/category/giving-feedback.svg',
      defaultContext: t('givingFeedback.defaultContext'),
      defaultGoal: t('givingFeedback.defaultGoal'),
      defaultOtherParty: t('givingFeedback.defaultOtherParty'),
    },
    {
      id: 'performance_reviews',
      name: t('performanceReviews.name'),
      iconUri: '/images/category/performance-reviews.svg',
      defaultContext: t('performanceReviews.defaultContext'),
      defaultGoal: t('performanceReviews.defaultGoal'),
      defaultOtherParty: t('performanceReviews.defaultOtherParty'),
    },
    {
      id: 'conflict_resolution',
      name: t('conflictResolution.name'),
      iconUri: '/images/category/conflict-resolution.svg',
      defaultContext: t('conflictResolution.defaultContext'),
      defaultGoal: t('conflictResolution.defaultGoal'),
      defaultOtherParty: t('conflictResolution.defaultOtherParty'),
    },
    {
      id: 'salary_discussions',
      name: t('salaryDiscussions.name'),
      iconUri: '/images/category/salary-discussions.svg',
      defaultContext: t('salaryDiscussions.defaultContext'),
      defaultGoal: t('salaryDiscussions.defaultGoal'),
      defaultOtherParty: t('salaryDiscussions.defaultOtherParty'),
    },
  ];
}
