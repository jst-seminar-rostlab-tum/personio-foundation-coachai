'use client';

import { useEffect, useState, useCallback } from 'react';
import { useTranslations } from 'next-intl';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { Button } from '@/components/ui/Button';
import { ArrowLeftIcon } from 'lucide-react';
import { Categories } from '@/lib/constants/categories';
import PersonaCollapsibleSection from '@/components/common/PersonaCollapsibleSection';
import { api } from '@/services/ApiClient';
import { showErrorToast } from '@/lib/utils/toast';
import { ConversationScenarioPreparation } from '@/interfaces/models/ConversationScenario';
import { conversationScenarioService } from '@/services/ConversationScenarioService';
import ResourcesList from '@/components/common/ResourcesList';
import EmptyListComponent from '@/components/common/EmptyListComponent';
import PreparationChecklist from './PreparationChecklist';
import ObjectivesList from './ObjectivesList';
import PreparationKeyConcepts from './PreparationKeyConcepts';
import { CreateSessionButton } from './CreateSessionButton';

export default function PreparationContent() {
  const t = useTranslations('Preparation');
  const tCommon = useTranslations('Common');
  const tConversationScenario = useTranslations('ConversationScenario');
  const tCategories = useTranslations('ConversationScenario.categories');
  const categories = Categories(tCategories);
  const [preparationData, setPreparationData] = useState<ConversationScenarioPreparation | null>(
    null
  );
  const [isLoading, setIsLoading] = useState(true);
  const params = useParams();
  const conversationScenarioId = params.id as string;

  const getTrainingPreparation = useCallback(
    async (id: string) => {
      try {
        const response = await conversationScenarioService.getPreparation(api, id);

        if (response.status === 202) {
          setTimeout(() => {
            getTrainingPreparation(id);
          }, 2000);
          return;
        }

        if (response.status === 200) {
          setPreparationData(response.data);
          setIsLoading(false);
          return;
        }

        throw new Error('Failed to get training case preparation data');
      } catch (error) {
        showErrorToast(error, t('getPreparationError'));
        setIsLoading(false);
        console.error(error);
      }
    },
    [t]
  );

  useEffect(() => {
    getTrainingPreparation(conversationScenarioId);
  }, [conversationScenarioId, getTrainingPreparation]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center w-full min-h-[400px]">
        <div className="flex flex-col items-center gap-4">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
          <p className="text-lg">{t('loadingText')}</p>
        </div>
      </div>
    );
  }

  const { categoryId, personaName, difficultyLevel } = preparationData || {};

  const categoryName = categories?.[categoryId as string]?.name;
  const personaKey = `customize.persona.personas.${personaName}`;
  const personaNameText = tConversationScenario(`${personaKey}.name`);
  const personaImgSrc = tConversationScenario(`${personaKey}.imageUri`);
  const difficultyLevelText = tConversationScenario(difficultyLevel ?? '');

  return (
    <>
      {preparationData && (
        <PersonaCollapsibleSection
          situationalFacts={preparationData?.situationalFacts}
          persona={preparationData?.persona}
          categoryName={categoryName}
          difficultyLevel={difficultyLevelText}
          personaName={personaNameText}
          imgSrc={personaImgSrc}
          difficultyLevelBadge={difficultyLevel}
        />
      )}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <section className="flex flex-col gap-6 w-full border border-bw-40 rounded-lg p-8">
          <div className="flex items-center gap-2">
            <h2 className="text-xl">{t('objectives')}</h2>
          </div>
          {preparationData && <ObjectivesList objectives={preparationData.objectives} />}
        </section>
        <section className="flex flex-col gap-6 w-full border border-bw-40 rounded-lg p-8">
          <div className="flex items-center gap-2">
            <h2 className="text-xl">{t('keyConcepts')}</h2>
          </div>
          {preparationData && <PreparationKeyConcepts keyConcepts={preparationData.keyConcepts} />}
        </section>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <section className="flex flex-col gap-6 w-full border border-bw-40 rounded-lg p-8">
          <div className="flex items-center gap-2">
            <h2 className="text-xl">{t('preparation')}</h2>
          </div>
          {preparationData && <PreparationChecklist checklist={preparationData.prepChecklist} />}
        </section>
        <section className="flex flex-col gap-6 w-full border border-bw-40 rounded-lg p-8">
          <div>
            <h2 className="text-xl">{tCommon('resources.title')}</h2>
            <p className="text-base text-bw-70">{tCommon('resources.subtitle')}</p>
          </div>
          {preparationData?.documentNames && preparationData.documentNames.length > 0 ? (
            <ResourcesList resources={preparationData.documentNames} />
          ) : (
            <EmptyListComponent itemType={tCommon('resources.title')} showBorder={false} />
          )}
        </section>
      </div>
      <div className="flex gap-4">
        <Link href="/new-conversation-scenario" className="flex-1">
          <Button size="full" variant="outline">
            <ArrowLeftIcon />
            {tCommon('back')}
          </Button>
        </Link>

        <CreateSessionButton scenarioId={conversationScenarioId} />
      </div>
    </>
  );
}
