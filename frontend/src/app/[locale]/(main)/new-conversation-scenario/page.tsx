import { generateMetadata as generateDynamicMetadata } from '@/lib/metadata';
import type { Metadata } from 'next';
import { MetadataProps } from '@/interfaces/MetadataProps';
import ConversationScenarioForm from './components/ConversationScenarioForm';

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/new-conversation-scenario', true);
}

export default function ConversationScenarioPage() {
  return <ConversationScenarioForm />;
}
