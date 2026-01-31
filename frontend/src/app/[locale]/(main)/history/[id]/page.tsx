import { Suspense } from 'react';
import { generateMetadata as generateDynamicMetadata } from '@/lib/utils/metadata';
import type { Metadata } from 'next';
import PersonaCollapsibleSection from '@/components/common/PersonaCollapsibleSection';
import { PagesProps } from '@/interfaces/props/PagesProps';
import { MetadataProps } from '@/interfaces/props/MetadataProps';
import { conversationScenarioService } from '@/services/ConversationScenarioService';
import { api } from '@/services/ApiServer';
import { getTranslations } from 'next-intl/server';
import { Categories } from '@/lib/constants/categories';
import { sessionService } from '@/services/SessionService';
import HistoryHeader from './components/HistoryHeader';
import Loading from './loading';
import HistoryTable from './components/HistoryTable';

/**
 * Generates localized metadata for the scenario history page.
 */
export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/history', true);
}

/**
 * Renders a scenario's history, stats, and session list.
 */
export default async function HistoryPage(props: PagesProps) {
  const { id } = await props.params;
  const PAGE_SIZE = 3;
  const conversationScenarioPromise = conversationScenarioService.getConversationScenario(api, id);
  const sessionsPromise = sessionService.getPaginatedSessions(api, 1, PAGE_SIZE, id);
  const [conversationScenario, sessions] = await Promise.all([
    conversationScenarioPromise,
    sessionsPromise,
  ]);
  const tConversationScenario = await getTranslations('ConversationScenario');
  const tCategories = await getTranslations('ConversationScenario.categories');
  const categories = Categories(tCategories);
  const {
    categoryId,
    personaName,
    difficultyLevel: difficultyLevelKey,
  } = conversationScenario.data ?? {};
  const categoryName = categories?.[categoryId]?.name ?? '';
  const personaKey = personaName ? `customize.persona.personas.${personaName}` : null;
  const personaDisplayName = personaKey ? tConversationScenario(`${personaKey}.name`) : '';
  const personaImgSrc = personaKey ? tConversationScenario(`${personaKey}.imageUri`) : '';
  const difficultyLevel = difficultyLevelKey ? tConversationScenario(difficultyLevelKey) : '';

  return (
    <Suspense fallback={<Loading />}>
      <div className="flex flex-col gap-12">
        <HistoryHeader scenarioId={id} />
        <PersonaCollapsibleSection
          situationalFacts={conversationScenario.data.situationalFacts}
          persona={conversationScenario.data.persona}
          categoryName={categoryName}
          difficultyLevel={difficultyLevel}
          personaName={personaDisplayName}
          imgSrc={personaImgSrc}
          difficultyLevelBadge={difficultyLevelKey}
        />
        <HistoryTable
          sessions={sessions.data.sessions}
          limit={sessions.data.limit}
          totalSessions={sessions.data.totalSessions}
          scenarioId={id}
        />
      </div>
    </Suspense>
  );
}
