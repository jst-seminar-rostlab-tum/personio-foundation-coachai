'use client';

import { useTranslations } from 'next-intl';
import Image from 'next/image';
import { ConversationCategory } from '@/interfaces/models/ConversationScenario';
import { CategoryButton } from './CategoryButton';

interface CategoryStepProps {
  selectedCategory: string;
  onCategorySelect: (category: ConversationCategory) => void;
  categories: ConversationCategory[];
}

export function CategoryStep({
  selectedCategory,
  onCategorySelect,
  categories,
}: CategoryStepProps) {
  const t = useTranslations('ConversationScenario.category');
  return (
    <div className="space-y-8">
      <div className="text-xl text-font-dark text-center">{t('title')}</div>
      <div className="flex flex-wrap justify-center gap-5 w-full max-w-4xl mx-auto">
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
            <span className="text-center">{category.name}</span>
          </CategoryButton>
        ))}
      </div>
    </div>
  );
}
