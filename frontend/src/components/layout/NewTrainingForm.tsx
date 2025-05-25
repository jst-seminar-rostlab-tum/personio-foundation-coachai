'use client';

import { Button } from '@/components/ui/button';
import { ArrowLeftIcon, ArrowRightIcon } from 'lucide-react';
import Stepper from '@/components/ui/stepper';
import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { FormState } from '@/interfaces/NewTrainingFormState';
import { CategoryStep } from './NewTrainingCategoryStep';
import { SituationStep } from './NewTrainingSituationStep';
import { CustomizeStep } from './NewTrainingCustomizeStep';

const initialFormState: FormState = {
  category: '',
  customCategory: '',
  party: {
    type: '',
    otherName: '',
  },
  context: '',
  goal: '',
  difficulty: '',
  emotionalTone: '',
  complexity: '',
};

export default function NewTrainingForm() {
  const t = useTranslations('NewTraining');
  const [currentStep, setCurrentStep] = useState(0);
  const [formState, setFormState] = useState<FormState>(initialFormState);
  const steps = [t('steps.category'), t('steps.situation'), t('steps.customize')];

  const handleStepClick = (step: number) => {
    if (step <= currentStep + 1) {
      setCurrentStep(step);
    }
  };

  const isStepValid = (step: number): boolean => {
    switch (step) {
      case 0:
        return !!formState.category;
      case 1:
        return (
          !!formState.party.type &&
          (formState.party.type !== 'other' || !!formState.party.otherName) &&
          !!formState.context &&
          !!formState.goal
        );
      case 2:
        return !!formState.difficulty && !!formState.emotionalTone && !!formState.complexity;
      default:
        return false;
    }
  };

  const handleCategorySelect = (category: string) => {
    setFormState((prev) => ({ ...prev, category }));
  };

  const handleCustomCategoryInput = (customCategory: string) => {
    setFormState((prev) => ({ ...prev, customCategory }));
  };

  const handlePartyChange = (type: string, otherName?: string) => {
    setFormState((prev) => ({
      ...prev,
      party: { type, otherName: otherName || prev.party.otherName },
    }));
  };

  const handleContextChange = (context: string) => {
    setFormState((prev) => ({ ...prev, context }));
  };

  const handleGoalChange = (goal: string) => {
    setFormState((prev) => ({ ...prev, goal }));
  };

  const handleDifficultyChange = (difficulty: string) => {
    setFormState((prev) => ({ ...prev, difficulty }));
  };

  const handleEmotionalToneChange = (emotionalTone: string) => {
    setFormState((prev) => ({ ...prev, emotionalTone }));
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
        onStepClick={handleStepClick}
        showAllStepNumbers
        showStepLabels
        className="p-2 mb-16"
      />

      {currentStep === 0 && (
        <CategoryStep
          selectedCategory={formState.category}
          onCategorySelect={handleCategorySelect}
        />
      )}

      {currentStep === 1 && (
        <SituationStep
          party={formState.party}
          context={formState.context}
          goal={formState.goal}
          onPartyChange={handlePartyChange}
          onContextChange={handleContextChange}
          onCustomCategoryInput={handleCustomCategoryInput}
          onGoalChange={handleGoalChange}
          category={formState.category}
          customCategory={formState.customCategory}
        />
      )}

      {currentStep === 2 && (
        <CustomizeStep
          difficulty={formState.difficulty}
          emotionalTone={formState.emotionalTone}
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
          onClick={() => setCurrentStep(() => currentStep + 1)}
          variant={!isStepValid(currentStep) ? 'disabled' : 'default'}
        >
          {currentStep === 2 ? t('navigation.create') : t('navigation.next')}
          <ArrowRightIcon />
        </Button>
      </div>
    </div>
  );
}
