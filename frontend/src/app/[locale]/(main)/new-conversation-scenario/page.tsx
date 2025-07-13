import { generateMetadata as generateDynamicMetadata } from '@/lib/utils/metadata';
import type { Metadata } from 'next';
import { MetadataProps } from '@/interfaces/props/MetadataProps';
import ConversationScenarioForm from './components/ConversationScenarioForm';

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/new-conversation-scenario', true);
}

export default async function ConversationScenarioPage() {
  return <ConversationScenarioForm />;
}
