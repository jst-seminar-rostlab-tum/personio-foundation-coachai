'use client';

import { Button } from '@/components/ui/Button';
import { ArrowLeftIcon, ArrowRightIcon } from 'lucide-react';
import Stepper from '@/components/common/Stepper';
import { use, useState } from 'react';
import { useTranslations } from 'next-intl';
import { ConversationCategory } from '@/interfaces/ConversationCategory';
import { FormState } from '@/interfaces/NewTrainingFormState';
import { TrainingCase } from '@/interfaces/TrainingCase';
import { createTrainingCase } from '@/services/CreateTrainingCase';
import { CategoryStep } from './CategoryStep';
import { SituationStep } from './SituationStep';
import { CustomizeStep } from './CustomizeStep';

const initialFormState: FormState = {
  category: '',
  customCategory: '',
  name: '',
  party: {
    type: '',
    otherName: '',
  },
  context: '',
  goal: '',
  difficulty: '',
  emotionalTone: '',
  complexity: '',
  isCustom: false,
};

export default function NewTrainingForm({
  categories,
}: {
  categories: Promise<ConversationCategory[]>;
}) {
  const t = useTranslations('NewTraining');
  const [currentStep, setCurrentStep] = useState(0);
  const [formState, setFormState] = useState<FormState>(initialFormState);
  const steps = [t('steps.category'), t('steps.situation'), t('steps.customize')];
  const allCategories = use(categories);
  console.log('allCategories', allCategories);
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
          (!formState.isCustom || !!formState.customCategory) &&
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

  const handleCategorySelect = (category: ConversationCategory) => {
    setFormState((prev) => ({
      ...prev,
      category: category.id,
      name: category.name,
      context: category.defaultContext || prev.context,
      goal: category.defaultGoal || prev.goal,
      party: {
        type: category.defaultOtherParty || prev.party.type,
        otherName: prev.party.otherName,
      },
      isCustom: category.isCustom || false,
    }));
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

  const submitForm = async () => {
    if (currentStep !== 2) {
      setCurrentStep(() => currentStep + 1);
      return;
    }

    const trainingCase: TrainingCase = {
      category_id: formState.category,
      custom_category_label: formState.customCategory,
      title: formState.name,
      context: formState.context,
      goal: formState.goal,
      other_party:
        formState.party.type === 'other' ? formState.party.otherName : formState.party.type,
      difficulty: formState.difficulty,
      complexity: formState.complexity,
      tone: formState.emotionalTone,
    };

    const response = await createTrainingCase(trainingCase);
    console.log(response);
    if (response.status === 201) {
      console.log('success');
    } else {
      console.log('error');
    }
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
          selectedCategory={formState.category}
          onCategorySelect={handleCategorySelect}
          categories={allCategories}
        />
      )}

      {currentStep === 1 && (
        <SituationStep
          party={formState.party.type}
          context={formState.context}
          goal={formState.goal}
          onPartyChange={handlePartyChange}
          onContextChange={handleContextChange}
          onCustomCategoryInput={handleCustomCategoryInput}
          onGoalChange={handleGoalChange}
          isCustom={formState.isCustom}
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
          onClick={() => submitForm()}
          variant={!isStepValid(currentStep) ? 'disabled' : 'default'}
        >
          {currentStep === 2 ? t('navigation.create') : t('navigation.next')}
          <ArrowRightIcon />
        </Button>
      </div>
    </div>
  );
}
