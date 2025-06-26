'use client';

import { Button } from '@/components/ui/Button';
import { ArrowLeftIcon, ArrowRightIcon } from 'lucide-react';
import Stepper from '@/components/common/Stepper';
import { useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
import { useParams, useRouter } from 'next/navigation';
import { ConversationScenarioFormProps } from '@/interfaces/ConversationScenarioFormProps';
import { ConversationCategory } from '@/interfaces/ConversationCategory';
import { ConversationScenario } from '@/interfaces/ConversationScenario';
import { conversationScenarioService } from '@/services/client/ConversationScenarioService';
import { showErrorToast } from '@/lib/toast';
import { useConversationScenarioStore } from '@/store/ConversationScenarioStore';
import { CategoryStep } from './CategoryStep';
import { SituationStep } from './SituationStep';
import { CustomizeStep } from './CustomizeStep';

export default function ConversationScenarioForm({
  categoriesData,
}: ConversationScenarioFormProps) {
  const t = useTranslations('ConversationScenario');
  const router = useRouter();
  const { locale } = useParams();

  const {
    step: currentStep,
    setStep,
    formState,
    updateForm,
    reset,
  } = useConversationScenarioStore();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [categories, setCategories] = useState<ConversationCategory[]>(
    t.raw('categories') as ConversationCategory[]
  );

  const steps = [t('steps.category'), t('steps.situation'), t('steps.customize')];

  useEffect(() => {
    setCategories((prev) =>
      prev.map((cat) => {
        const match = categoriesData.find((f: ConversationCategory) => f.id === cat.id);
        return match ? { ...cat, defaultContext: match.defaultContext } : cat;
      })
    );
  }, [categoriesData]);

  const handleStepClick = (step: number) => {
    if (step <= currentStep + 1) {
      setStep(step);
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

  const submitForm = async () => {
    if (currentStep !== 2) {
      setStep(currentStep + 1);
      return;
    }

    if (isSubmitting) return;

    setIsSubmitting(true);

    const scenario: ConversationScenario = {
      categoryId: formState.category,
      customCategoryLabel: formState.customCategory,
      context: formState.context,
      goal: formState.goal,
      otherParty: formState.otherParty,
      difficultyLevel: formState.difficulty,
      tone: formState.emotionalTone,
      complexity: formState.complexity,
      languageCode: locale as string,
    };

    try {
      const { data } = await conversationScenarioService.createConversationScenario(scenario);
      router.push(`/preparation/${data.scenarioId}`);
      setTimeout(reset, 2000);
    } catch (error) {
      showErrorToast(error, t('errorMessage'));
      setIsSubmitting(false);
    }
  };

  const getButtonText = () => {
    if (isSubmitting && currentStep === 2) {
      return t('navigation.creating');
    }
    if (currentStep === 2) {
      return t('navigation.create');
    }
    return t('navigation.next');
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
          onCategorySelect={(category) =>
            updateForm({
              category: category.id,
              name: category.name,
              context: category.defaultContext || '',
              goal: category.defaultGoal || '',
              otherParty: category.defaultOtherParty || '',
              isCustom: category.isCustom || false,
            })
          }
          categories={categories}
        />
      )}

      {currentStep === 1 && (
        <SituationStep
          otherParty={formState.otherParty}
          context={formState.context}
          goal={formState.goal}
          onPartyChange={(val) => updateForm({ otherParty: val })}
          onContextChange={(val) => updateForm({ context: val })}
          onGoalChange={(val) => updateForm({ goal: val })}
          onCustomCategoryInput={(val) => updateForm({ customCategory: val })}
          isCustom={formState.isCustom}
          customCategory={formState.customCategory}
        />
      )}

      {currentStep === 2 && (
        <CustomizeStep
          difficulty={formState.difficulty}
          emotionalTone={formState.emotionalTone}
          complexity={formState.complexity}
          onDifficultyChange={(val) => updateForm({ difficulty: val })}
          onEmotionalToneChange={(val) => updateForm({ emotionalTone: val })}
          onComplexityChange={(val) => updateForm({ complexity: val })}
        />
      )}

      <div className="flex gap-4 w-full justify-center mt-8 max-w-4xl mx-auto">
        {currentStep !== 0 && (
          <Button
            size="full"
            variant="outline"
            onClick={() => setStep(currentStep - 1)}
            disabled={currentStep === 0}
          >
            <ArrowLeftIcon />
            {t('navigation.back')}
          </Button>
        )}
        <Button
          size="full"
          onClick={submitForm}
          variant={isSubmitting || !isStepValid(currentStep) ? 'disabled' : 'default'}
          disabled={isSubmitting || !isStepValid(currentStep)}
        >
          {getButtonText()}
          <ArrowRightIcon />
        </Button>
      </div>
    </div>
  );
}
