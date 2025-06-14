'use client';

import { useEffect, useState, useCallback } from 'react';
import ObjectivesList from '@/app/[locale]/(main)/preparation/components/ObjectivesList';
import PreparationChecklist from '@/app/[locale]/(main)/preparation/components/PreparationChecklist';
import { useTranslations } from 'next-intl';
import { TrainingPreparation } from '@/interfaces/TrainingPreparation';
import { useParams } from 'next/navigation';
import { conversationScenarioService } from '@/services/ConversationScenarioService';
import PreparationKeyConcepts from './PreparationKeyConcepts';

export default function PreparationPage() {
  const t = useTranslations('Preparation');
  const [preparationData, setPreparationData] = useState<TrainingPreparation | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const params = useParams();
  const trainingCaseId = params.id as string;

  const getTrainingPreparation = useCallback(
    async (id: string) => {
      try {
        const response = await conversationScenarioService.getPreparation(id);

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
    },
    [setPreparationData, setIsLoading]
  );

  useEffect(() => {
    getTrainingPreparation(trainingCaseId);
  }, [getTrainingPreparation, trainingCaseId]);

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
  );
}
