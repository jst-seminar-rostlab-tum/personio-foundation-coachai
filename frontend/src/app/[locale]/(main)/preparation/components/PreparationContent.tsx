'use client';

import { useEffect, useState, useCallback } from 'react';
import api from '@/services/Api';
import ObjectivesList from '@/app/[locale]/(main)/preparation/components/ObjectivesList';
import PreparationChecklist from '@/app/[locale]/(main)/preparation/components/PreparationChecklist';
import { useTranslations } from 'next-intl';

type KeyConcept = {
  header: string;
  value: string;
};

type TrainingPreparation = {
  id: string;
  caseId: string;
  objectives: string[];
  keyConcepts: KeyConcept[];
  prepChecklist: string[];
  status: string;
  createdAt: string;
  updatedAt: string;
};

export default function PreparationPage() {
  const t = useTranslations('Preparation');
  const [preparationData, setPreparationData] = useState<TrainingPreparation | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const getTrainingPreparation = useCallback(async () => {
    try {
      // TODO: Determine the training case ID dynamically in the future
      const trainingCase = 'cd76c086-70d5-4a9f-bddc-d4e6ee9631ac';
      const response = await api.get(`/training-case/${trainingCase}/preparation`);

      if (response.status === 202) {
        // If status is 202, wait for 2 seconds and try again
        setTimeout(() => {
          getTrainingPreparation();
        }, 2000);
        return;
      }

      if (response.status === 200) {
        setPreparationData(response.data);
        setIsLoading(false);
        return;
      }

      throw new Error('Failed to get training case preparation data');
    } catch (error: unknown) {
      setIsLoading(false);
      let errorMessage = 'ERROR';

      if (error && typeof error === 'object' && 'response' in error) {
        const err = error as { response?: { status?: number } };
        switch (err.response?.status) {
          case 401:
            errorMessage = '401';
            break;
          case 403:
            errorMessage = '403';
            break;
          case 404:
            errorMessage = '404';
            break;
          case 500:
            errorMessage = '500';
            break;
          default:
            errorMessage = 'ERROR';
            break;
        }
      }
      console.error(errorMessage);
    }
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      await getTrainingPreparation();
    };
    fetchData();
  }, [getTrainingPreparation]);

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
    <div className="flex flex-col md:flex-row gap-4 items-stretch">
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
    </div>
  );
}
