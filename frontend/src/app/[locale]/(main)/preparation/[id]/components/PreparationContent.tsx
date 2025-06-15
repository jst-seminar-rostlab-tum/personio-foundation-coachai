'use client';

import { useEffect, useState, useCallback } from 'react';
import { useTranslations } from 'next-intl';
import { useParams } from 'next/navigation';
import { api } from '@/services/ApiClient';
import { conversationScenarioService } from '@/services/ConversationScenarioService';
import { ConversationScenarioPreparation } from '@/interfaces/ConversationScenario';
import PreparationChecklist from './PreparationChecklist';
import ObjectivesList from './ObjectivesList';
import PreparationKeyConcepts from './PreparationKeyConcepts';

export default function PreparationContent() {
  const t = useTranslations('Preparation');
  const [preparationData, setPreparationData] = useState<ConversationScenarioPreparation | null>(
    null
  );
  const [isLoading, setIsLoading] = useState(true);
  const params = useParams();
  const conversationScenarioId = params.id as string;

  const getTrainingPreparation = useCallback(async (id: string) => {
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
      setIsLoading(false);
      console.error(error);
    }
  }, []);

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

  return (
    <>
      {preparationData && (
        <section className="flex flex-col gap-4 bg-marigold-5 border border-marigold-30 rounded-lg p-8 text-marigold-95">
          <h2 className="text-xl">{preparationData.categoryName}</h2>
          <div className="text-base italic leading-loose">{preparationData.context}</div>
        </section>
      )}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <section className="flex flex-col gap-4 w-full border border-bw-20 rounded-lg p-8">
          <div className="flex items-center gap-2">
            <h2 className="text-xl">{t('objectives.title')}</h2>
          </div>
          {preparationData && <ObjectivesList objectives={preparationData.objectives} />}
        </section>

        <section className="flex flex-col gap-4 w-full border border-bw-20 rounded-lg p-8">
          <div className="flex items-center gap-2">
            <h2 className="text-xl">{t('preparation.title')}</h2>
          </div>
          {preparationData && <PreparationChecklist checklist={preparationData.prepChecklist} />}
        </section>
        <section className="flex flex-col gap-4 w-full border border-bw-20 rounded-lg p-8">
          <div className="flex items-center gap-2">
            <h2 className="text-xl">{t('keyConcepts.title')}</h2>
          </div>
          {preparationData && <PreparationKeyConcepts keyConcepts={preparationData.keyConcepts} />}
        </section>
        <section className="flex flex-col gap-4 w-full border border-bw-20 rounded-lg p-8">
          <h2 className="text-xl">{t('resources.title')}</h2>
        </section>
      </div>
    </>
  );
}
