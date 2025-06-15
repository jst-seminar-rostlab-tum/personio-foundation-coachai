import { ConversationCategory } from './ConversationCategory';

export interface CategoryStepProps {
  selectedCategory: string;
  onCategorySelect: (category: ConversationCategory) => void;
  categories: ConversationCategory[];
}
