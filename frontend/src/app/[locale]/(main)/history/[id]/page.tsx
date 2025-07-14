import { Suspense } from 'react';
import { generateMetadata as generateDynamicMetadata } from '@/lib/utils/metadata';
import type { Metadata } from 'next';
import PersonaCollapsibleSection from '@/components/common/PersonaCollapsibleSection';
import { PagesProps } from '@/interfaces/props/PagesProps';
import { MetadataProps } from '@/interfaces/props/MetadataProps';
import { UserProfileService } from '@/services/UserProfileService';
import { conversationScenarioService } from '@/services/ConversationScenarioService';
import { api } from '@/services/ApiServer';
import { getTranslations } from 'next-intl/server';
import { Categories } from '@/lib/constants/categories';
import { sessionService } from '@/services/SessionService';
import HistoryHeader from './components/HistoryHeader';
import Loading from './loading';
import HistoryTable from './components/HistoryTable';
import HistoryStats from './components/HistoryStats';

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/history', true);
}

export default async function HistoryPage(props: PagesProps) {
  const { id } = await props.params;
  const conversationScenarioPromise = conversationScenarioService.getConversationScenario(api, id);
  const userStatsPromise = UserProfileService.getUserStats(api);
  const sessionsPromise = sessionService.getPaginatedSessions(api, 1, 10, id);
  const [conversationScenario, userStats, sessions] = await Promise.all([
    conversationScenarioPromise,
    userStatsPromise,
    sessionsPromise,
  ]);

  const tConversationScenario = await getTranslations('ConversationScenario');
  const tCategories = await getTranslations('ConversationScenario.categories');
  const categories = Categories(tCategories);
  const categoryName = categories[conversationScenario.data.categoryId].name;
  const personaName = tConversationScenario(
    `customize.persona.personas.${conversationScenario.data.personaName}.name`
  );
  const personaImgSrc = tConversationScenario(
    `customize.persona.personas.${conversationScenario.data.personaName}.imageUri`
  );
  const difficultyLevel = tConversationScenario(`${conversationScenario.data.difficultyLevel}`);

  return (
    <Suspense fallback={<Loading />}>
      <div className="flex flex-col gap-12">
        <HistoryHeader scenarioId={id} />
        <PersonaCollapsibleSection
          situationalFacts={conversationScenario.data.situationalFacts}
          persona={conversationScenario.data.persona}
          categoryName={categoryName}
          difficultyLevel={difficultyLevel}
          personaName={personaName}
          imgSrc={personaImgSrc}
        />
        <HistoryStats stats={userStats} />
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
