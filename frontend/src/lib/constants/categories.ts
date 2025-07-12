import { ConversationCategory } from '@/interfaces/models/ConversationScenario';
import { useTranslations } from 'next-intl';

export function Categories(): Record<string, ConversationCategory> {
  const t = useTranslations('ConversationScenario.categories');
  return {
    giving_feedback: {
      id: 'giving_feedback',
      name: t('givingFeedback.name'),
      iconUri: '/images/category/giving-feedback.svg',
      defaultContext: t('givingFeedback.defaultContext'),
    },
    performance_reviews: {
      id: 'performance_reviews',
      name: t('performanceReviews.name'),
      iconUri: '/images/category/performance-reviews.svg',
      defaultContext: t('performanceReviews.defaultContext'),
    },
    conflict_resolution: {
      id: 'conflict_resolution',
      name: t('conflictResolution.name'),
      iconUri: '/images/category/conflict-resolution.svg',
      defaultContext: t('conflictResolution.defaultContext'),
    },
    salary_discussions: {
      id: 'salary_discussions',
      name: t('salaryDiscussions.name'),
      iconUri: '/images/category/salary-discussions.svg',
      defaultContext: t('salaryDiscussions.defaultContext'),
    },
  };
}
