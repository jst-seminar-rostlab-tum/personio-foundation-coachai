'use client';

import { Button } from '@/components/ui/Button';
import { ArrowLeftIcon, ArrowRightIcon } from 'lucide-react';
import Stepper from '@/components/common/Stepper';
import { use, useState } from 'react';
import { useTranslations } from 'next-intl';
import { useRouter } from 'next/navigation';
import { ConversationCategory } from '@/interfaces/ConversationCategory';
import { FormState } from '@/interfaces/NewTrainingFormState';
import { ConversationScenario } from '@/interfaces/ConversationScenario';
import { createConversationScenario } from '@/services/ConversationScenarioService';
import { CategoryStep } from './CategoryStep';
import { SituationStep } from './SituationStep';
import { CustomizeStep } from './CustomizeStep';

const initialFormState: FormState = {
  category: '',
  customCategory: '',
  name: '',
  otherParty: '',
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
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(0);
  const [formState, setFormState] = useState<FormState>(initialFormState);
  const steps = [t('steps.category'), t('steps.situation'), t('steps.customize')];
  const allCategories = use(categories);

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
          !!formState.otherParty &&
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
      otherParty: category.defaultOtherParty || '',
      isCustom: category.isCustom || false,
    }));
  };

  const handleCustomCategoryInput = (customCategory: string) => {
    setFormState((prev) => ({ ...prev, customCategory }));
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

    // TODO: get user id from auth
    const userId = '53b5bda9-44c8-4a52-a664-f8175b79c664'; // TODO: Remove this after getting auth

    const scenario: ConversationScenario = {
      userId,
      categoryId: formState.category,
      customCategoryLabel: formState.customCategory,
      context: formState.context,
      goal: formState.goal,
      otherParty: formState.otherParty,
      difficultyId: formState.difficulty,
      tone: formState.emotionalTone,
      complexity: formState.complexity,
      status: 'draft',
    };

    try {
      const response = await createConversationScenario(scenario);
      router.push(`/preparation/${response.id}`);
    } catch (error) {
      console.error('Error:', error);
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
          otherParty={formState.otherParty}
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
