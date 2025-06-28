import { generateMetadata as generateDynamicMetadata } from '@/lib/metadata';
import type { Metadata } from 'next';
import { MetadataProps } from '@/interfaces/props/MetadataProps';
import { conversationScenarioService } from '@/services/ConversationScenarioService';
import { api } from '@/services/ApiServer';
import ConversationScenarioForm from './components/ConversationScenarioForm';

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/new-conversation-scenario', true);
}

export default async function ConversationScenarioPage() {
  const categories = await conversationScenarioService.getConversationCategories(api);
  return <ConversationScenarioForm categoriesData={categories.data} />;
}
