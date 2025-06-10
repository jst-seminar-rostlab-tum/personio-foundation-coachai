'use client';

import { useTranslations } from 'next-intl';
import Image from 'next/image';
import { CategoryStepProps } from '@/interfaces/CategoryStepProps';
import { CategoryButton } from './CategoryButton';

export function CategoryStep({
  selectedCategory,
  onCategorySelect,
  categories,
}: CategoryStepProps) {
  const t = useTranslations('NewTraining.category');
  return (
    <div className="space-y-8">
      <div className="text-xl text-font-dark text-center">{t('title')}</div>
      <div className="grid grid-cols-2 px-2 md:grid-cols-3 gap-5 w-full mx-auto place-items-center lg:grid-cols-5">
        {categories.map((category) => (
          <CategoryButton
            key={category.id}
            onClick={() => onCategorySelect(category)}
            selected={selectedCategory === category.id}
          >
            <Image
              src={category.iconUri}
              alt={category.name}
              width={56}
              height={56}
              className="mb-4"
            />
            {category.name}
          </CategoryButton>
        ))}
      </div>
    </div>
  );
}
