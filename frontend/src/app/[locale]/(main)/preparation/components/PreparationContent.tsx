'use client';

import { useEffect, useState } from 'react';
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

  const getTrainingPreparation = async () => {
    try {
      // TODO: Determine the training case ID dynamically in the future:q
      const trainingCase = '454cdf80-7937-4844-89bc-dae1edc2da81';
      const response = await api.get(`/training-case/${trainingCase}/preparation`);

      if (response.status !== 200) {
        throw new Error('Failed to get training case preparation data');
      }

      setPreparationData(response.data);
    } catch (err) {
      let errorMessage = 'ERROR';
      if (err.response) {
        switch (err.response.status) {
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
  };

  useEffect(() => {
    getTrainingPreparation();
  }, []);

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
