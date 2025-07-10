'use client';

import { useEffect, useState, useCallback } from 'react';
import { useTranslations } from 'next-intl';
import { useParams } from 'next/navigation';
import { api } from '@/services/ApiClient';
import { showErrorToast } from '@/lib/utils/toast';
import { ConversationScenarioPreparation } from '@/interfaces/models/ConversationScenario';
import { Resource } from '@/interfaces/models/Resource';
import { conversationScenarioService } from '@/services/ConversationScenarioService';
import { getDocsSignedUrl } from '@/services/SignedUrlService';
import ResourcesList from '../../../../../../components/common/ResourcesList';
import PreparationChecklist from './PreparationChecklist';
import ObjectivesList from './ObjectivesList';
import PreparationKeyConcepts from './PreparationKeyConcepts';

export default function PreparationContent() {
  const t = useTranslations('Preparation');
  const tCommon = useTranslations('Common');
  const [preparationData, setPreparationData] = useState<ConversationScenarioPreparation | null>(
    null
  );
  const [isLoading, setIsLoading] = useState(true);
  const [resources, setResources] = useState<Resource[]>([]);
  const [resourcesLoading, setResourcesLoading] = useState(false);
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

  const convertDocumentNamesToResources = useCallback(
    async (documentNames: string[]): Promise<Resource[]> => {
      const resourcePromises = documentNames.map(async (docName) => {
        try {
          const response = await getDocsSignedUrl(api, docName);
          return {
            name: docName,
            author: '', // Change this in future (if backend supports it)
            fileUrl: response.url,
          };
        } catch (error) {
          console.error(`Failed to get signed URL for ${docName}:`, error);
          return {
            name: docName,
            author: '',
            fileUrl: docName,
          };
        }
      });

      return Promise.all(resourcePromises);
    },
    []
  );

  useEffect(() => {
    getTrainingPreparation(conversationScenarioId);
  }, [conversationScenarioId, getTrainingPreparation]);

  useEffect(() => {
    if (preparationData?.documentNames && preparationData.documentNames.length > 0) {
      setResourcesLoading(true);
      convertDocumentNamesToResources(preparationData.documentNames)
        .then((convertedResources) => {
          setResources(convertedResources);
          setResourcesLoading(false);
        })
        .catch((error) => {
          console.error('Error converting document names to resources:', error);
          setResourcesLoading(false);
        });
    } else {
      setResources([]);
    }
  }, [preparationData?.documentNames, convertDocumentNamesToResources]);

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
        {/* Objectives */}
        <section className="flex flex-col gap-4 w-full border border-bw-20 rounded-lg p-8">
          <div className="flex items-center gap-2">
            <h2 className="text-xl">{t('objectives')}</h2>
          </div>
          {preparationData && <ObjectivesList objectives={preparationData.objectives} />}
        </section>
        {/* Preparation Checklist */}
        <section className="flex flex-col gap-4 w-full border border-bw-20 rounded-lg p-8">
          <div className="flex items-center gap-2">
            <h2 className="text-xl">{t('preparation')}</h2>
          </div>
          {preparationData && <PreparationChecklist checklist={preparationData.prepChecklist} />}
        </section>
      </div>
      {/* Key Concepts */}
      <section className="flex flex-col gap-8 w-full border border-bw-20 rounded-lg p-8">
        <div className="flex items-center gap-2">
          <h2 className="text-xl">{t('keyConcepts')}</h2>
        </div>
        {preparationData && <PreparationKeyConcepts keyConcepts={preparationData.keyConcepts} />}
      </section>

      {/* Resources Section */}
      <section className="flex flex-col gap-4 mt-8 w-full">
        <div>
          <h2 className="text-xl">{tCommon('resources.title')}</h2>
          <p className="text-base text-bw-40">{tCommon('resources.subtitle')}</p>
        </div>

        {(() => {
          if (resourcesLoading) {
            return (
              <div className="flex items-center justify-center w-full min-h-[200px]">
                <div className="flex flex-col items-center gap-4">
                  <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary"></div>
                  <p className="text-base">{tCommon('resources.loading')}</p>
                </div>
              </div>
            );
          }

          if (resources.length > 0) {
            return <ResourcesList resources={resources} />;
          }

          return (
            <div className="flex items-center justify-center w-full min-h-[200px] border border-bw-20 rounded-lg">
              <p className="text-base text-bw-40">{tCommon('resources.noResources')}</p>
            </div>
          );
        })()}
      </section>
    </>
  );
}
