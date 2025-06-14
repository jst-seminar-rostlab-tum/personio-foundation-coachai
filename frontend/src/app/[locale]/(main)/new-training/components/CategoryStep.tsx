'use client';

import { useTranslations } from 'next-intl';
import Image from 'next/image';
import { CategoryStepProps } from '@/interfaces/CategoryStepProps';
import { CategoryButton } from './CategoryButton';

export function CategoryStep({ selectedCategory, onCategorySelect }: CategoryStepProps) {
  const t = useTranslations('NewTraining.category');

  return (
    <div className="space-y-8">
      <div className="text-xl text-font-dark text-center">{t('title')}</div>
      <div className="grid grid-cols-2 px-2 md:grid-cols-3 gap-5 w-full mx-auto place-items-center lg:grid-cols-5">
        <CategoryButton
          onClick={() => onCategorySelect('giving_feedback')}
          selected={selectedCategory === 'feedback'}
        >
          <Image
            src="/icons/giving_feedback.svg"
            alt={t('options.feedback')}
            width={56}
            height={56}
            className="mb-4"
          />
          {t('options.feedback')}
        </CategoryButton>
        <CategoryButton
          onClick={() => onCategorySelect('conflict_resolution')}
          selected={selectedCategory === 'conflict'}
        >
          <Image
            src="/icons/conflict_resolution.svg"
            alt={t('options.conflict')}
            width={56}
            height={56}
            className="mb-4"
          />
          {t('options.conflict')}
        </CategoryButton>
        <CategoryButton
          onClick={() => onCategorySelect('performance_reviews')}
          selected={selectedCategory === 'performance'}
        >
          <Image
            src="/icons/performance_reviews.svg"
            alt={t('options.performance')}
            width={56}
            height={56}
            className="mb-4"
          />
          {t('options.performance')}
        </CategoryButton>
        <CategoryButton
          onClick={() => onCategorySelect('salary_discussions')}
          selected={selectedCategory === 'salary'}
        >
          <Image
            src="/icons/salary_discussions.svg"
            alt={t('options.salary')}
            width={56}
            height={56}
            className="mb-4"
          />
          {t('options.salary')}
        </CategoryButton>
      </div>
    </div>
  );
}
