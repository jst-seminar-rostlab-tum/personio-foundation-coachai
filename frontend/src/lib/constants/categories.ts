import { ConversationCategory } from '@/interfaces/models/ConversationScenario';
import { useTranslations } from 'next-intl';

export function Categories(): ConversationCategory[] {
  const t = useTranslations('ConversationScenario.categories');
  return [
    {
      id: 'giving_feedback',
      name: t('givingFeedback.name'),
      iconUri: '/images/category/giving-feedback.svg',
      description: t('givingFeedback.description'),
    },
    {
      id: 'performance_reviews',
      name: t('performanceReviews.name'),
      iconUri: '/images/category/performance-reviews.svg',
      description: t('performanceReviews.description'),
    },
    {
      id: 'conflict_resolution',
      name: t('conflictResolution.name'),
      iconUri: '/images/category/conflict-resolution.svg',
      description: t('conflictResolution.description'),
    },
    {
      id: 'salary_discussions',
      name: t('salaryDiscussions.name'),
      iconUri: '/images/category/salary-discussions.svg',
      description: t('salaryDiscussions.description'),
    },
  ];
}
