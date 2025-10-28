'use client';

import { Button } from '@/components/ui/Button';
import { ArrowLeftIcon, ArrowRightIcon } from 'lucide-react';
import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { useParams, useRouter } from 'next/navigation';
import { conversationScenarioService } from '@/services/ConversationScenarioService';
import { showErrorToast } from '@/lib/utils/toast';
import { ConversationScenario } from '@/interfaces/models/ConversationScenario';
import { useConversationScenarioStore } from '@/store/ConversationScenarioStore';
import { api } from '@/services/ApiClient';
import Stepper from '@/components/common/Stepper';
import { CategoryStep } from './CategoryStep';
import { CustomizeStep } from './CustomizeStep';
import ContextCardButtons from './ContextCardButtons';

export default function ConversationScenarioForm() {
  const t = useTranslations('ConversationScenario');
  const tCommon = useTranslations('Common');
  const router = useRouter();
  const { locale } = useParams();

  const { step: currentStep, setStep, formState, reset } = useConversationScenarioStore();

  const [isSubmitting, setIsSubmitting] = useState(false);

  const isStepValid = (step: number): boolean => {
    switch (step) {
      case 0:
        return !!formState.contextMode;
      case 1:
        return !!formState.category && !!formState.situationalFacts;
      case 2:
        return !!formState.difficulty && !!formState.persona;
      default:
        return false;
    }
  };

  const submitForm = async () => {
    if (currentStep !== 2) {
      setStep(currentStep + 1);
      return;
    }

    if (isSubmitting) return;

    setIsSubmitting(true);

    const scenario: ConversationScenario = {
      categoryId: formState.category,
      difficultyLevel: formState.difficulty,
      persona: formState.personaDescription,
      situationalFacts: formState.situationalFacts,
      languageCode: locale as string,
      personaName: formState.persona,
    };

    try {
      const { data } = await conversationScenarioService.createConversationScenario(api, scenario);
      router.push(`/preparation/${data.scenarioId}`);
      setTimeout(reset, 4000);
    } catch (error) {
      showErrorToast(error, t('errorMessage'));
      setIsSubmitting(false);
    }
  };

  return (
    <div className="pb-8">
      <h1 className="text-2xl text-font-dark text-center w-full mb-8">{t('title')}</h1>
      <Stepper
        steps={[t('customizationTitle'), t('situationTitle'), t('chooseOtherParty')]}
        currentStep={currentStep}
        showAllStepNumbers={true}
        showStepLabels={false}
        className="mb-8 sm:w-3/4 mx-auto"
      />

      {currentStep === 0 && <ContextCardButtons />}

      {currentStep === 1 && <CategoryStep />}

      {currentStep === 2 && <CustomizeStep />}

      <div className="fixed bottom-0 left-0 w-full z-50 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-[clamp(1.25rem,4vw,4rem)] py-6 flex gap-4 justify-center">
          {currentStep > 0 && (
            <Button size="full" variant="outline" onClick={() => setStep(currentStep - 1)}>
              <ArrowLeftIcon />
              {tCommon('back')}
            </Button>
          )}
          <Button
            size="full"
            onClick={currentStep < 2 ? () => setStep(currentStep + 1) : submitForm}
            variant={isSubmitting || !isStepValid(currentStep) ? 'disabled' : 'default'}
            disabled={isSubmitting || !isStepValid(currentStep)}
          >
            {currentStep < 2 ? tCommon('next') : t('create')}
            <ArrowRightIcon />
          </Button>
        </div>
      </div>
    </div>
  );
}
