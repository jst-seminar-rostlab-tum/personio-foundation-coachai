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
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-5 w-full mx-auto">
        {categories.map((category) => (
          <CategoryButton
            key={category.id}
            onClick={() => onCategorySelect(category)}
            selected={selectedCategory === category.id}
            className="w-full"
          >
            <div className="relative w-1/4 min-w-20 max-w-24 aspect-square mb-4">
              <Image src={category.iconUri} alt={category.name} fill className="object-contain" />
            </div>
            {category.name}
            {category.description}
          </CategoryButton>
        ))}
      </div>
    </div>
  );
}
