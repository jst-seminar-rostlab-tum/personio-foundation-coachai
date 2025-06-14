'use client';

import { Button } from '@/components/ui/Button';
import { AlertCircleIcon, ArrowLeftIcon, ArrowRightIcon } from 'lucide-react';
import Stepper from '@/components/common/Stepper';
import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { ConversationScenarioCreateResponse, FormState } from '@/interfaces/NewTraining';
import { createConversationScenario } from '@/services/NewTraining';
import { Alert, AlertTitle } from '@/components/ui/Alert';
import { CategoryStep } from './CategoryStep';
import { SituationStep } from './SituationStep';
import { CustomizeStep } from './CustomizeStep';

const initialFormState: FormState = {
  categoryId: '',
  otherParty: '',
  context: '',
  goal: '',
  difficultyLevel: '',
  tone: '',
  complexity: '',
};

export default function NewTrainingForm() {
  const t = useTranslations('NewTraining');
  const [currentStep, setCurrentStep] = useState(0);
  const [formState, setFormState] = useState<FormState>(initialFormState);
  const steps = [t('steps.category'), t('steps.situation'), t('steps.customize')];
  const [error, setError] = useState<string | null>(null);

  const handleStepClick = (step: number) => {
    if (step <= currentStep + 1) {
      setCurrentStep(step);
    }
  };

  const handleSubmit = async () => {
    setCurrentStep(() => currentStep + 1);
    if (currentStep === 2) {
      try {
        const response: ConversationScenarioCreateResponse =
          await createConversationScenario(formState);
        console.debug('Training scenario created successfully:', response);
      } catch (err) {
        console.error('Error creating training scenario: ', err);
        setError('An error occurred while creating the training scenario. Please try again later.');
      }
    }
  };

  const isStepValid = (step: number): boolean => {
    switch (step) {
      case 0:
        return !!formState.categoryId;
      case 1:
        return !!formState.otherParty && !!formState.context && !!formState.goal;
      case 2:
        return !!formState.difficultyLevel && !!formState.tone && !!formState.complexity;
      default:
        return false;
    }
  };

  const handleCategorySelect = (categoryId: string) => {
    setFormState((prev) => ({ ...prev, categoryId }));
  };

  const handlePartyChange = (otherParty: string) => {
    setFormState((prev) => ({
      ...prev,
      otherParty,
    }));
  };

  const handleContextChange = (context: string) => {
    setFormState((prev) => ({ ...prev, context }));
  };

  const handleGoalChange = (goal: string) => {
    setFormState((prev) => ({ ...prev, goal }));
  };

  const handleDifficultyChange = (difficultyLevel: string) => {
    setFormState((prev) => ({ ...prev, difficultyLevel }));
  };

  const handleEmotionalToneChange = (tone: string) => {
    setFormState((prev) => ({ ...prev, tone }));
  };

  const handleComplexityChange = (complexity: string) => {
    setFormState((prev) => ({ ...prev, complexity }));
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-2xl text-font-dark text-center w-full mb-8">{t('title')}</div>
      <Stepper
        steps={steps}
        currentStep={currentStep}
        showAllStepNumbers
        showStepLabels
        className="px-6 py-2 mb-16"
        onStepClick={handleStepClick}
        currentStepValid={isStepValid(currentStep)}
      />

      {currentStep === 0 && (
        <CategoryStep
          selectedCategory={formState.categoryId}
          onCategorySelect={handleCategorySelect}
        />
      )}

      {currentStep === 1 && (
        <SituationStep
          party={formState.otherParty}
          context={formState.context}
          goal={formState.goal}
          onPartyChange={handlePartyChange}
          onContextChange={handleContextChange}
          onGoalChange={handleGoalChange}
          category={formState.categoryId}
        />
      )}

      {currentStep === 2 && (
        <CustomizeStep
          difficulty={formState.difficultyLevel}
          emotionalTone={formState.tone}
          complexity={formState.complexity}
          onDifficultyChange={handleDifficultyChange}
          onEmotionalToneChange={handleEmotionalToneChange}
          onComplexityChange={handleComplexityChange}
        />
      )}

      <div className="flex gap-4 w-full justify-center mt-8 max-w-4xl mx-auto">
        {currentStep !== 0 && (
          <Button
            size="full"
            variant="outline"
            onClick={() => setCurrentStep(() => currentStep - 1)}
            disabled={currentStep === 0}
          >
            <ArrowLeftIcon />
            {t('navigation.back')}
          </Button>
        )}
        <Button
          size="full"
          onClick={handleSubmit}
          variant={!isStepValid(currentStep) ? 'disabled' : 'default'}
        >
          {currentStep === 2 ? t('navigation.create') : t('navigation.next')}
          <ArrowRightIcon />
        </Button>
      </div>
      {error && (
        <Alert variant="destructive">
          <AlertCircleIcon />
          <AlertTitle>{error}</AlertTitle>
        </Alert>
      )}
    </div>
  );
}
