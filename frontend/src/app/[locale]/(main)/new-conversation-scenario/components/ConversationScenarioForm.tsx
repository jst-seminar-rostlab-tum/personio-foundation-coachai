'use client';

import { Button } from '@/components/ui/Button';
import { ArrowLeftIcon, ArrowRightIcon } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
import { useParams, useRouter } from 'next/navigation';
import { Persona } from '@/interfaces/Persona';
import { conversationScenarioService } from '@/services/ConversationScenarioService';
import { showErrorToast } from '@/lib/utils/toast';
import {
  ConversationScenario,
  ConversationCategory,
} from '@/interfaces/models/ConversationScenario';
import { useConversationScenarioStore } from '@/store/ConversationScenarioStore';
import { api } from '@/services/ApiClient';
import { Categories } from '@/lib/constants/categories';
import { CategoryStep } from './CategoryStep';
import { CustomizeStep } from './CustomizeStep';

interface ConversationScenarioFormProps {
  categoriesData: ConversationCategory[];
}

export default function ConversationScenarioForm({
  categoriesData,
}: ConversationScenarioFormProps) {
  const t = useTranslations('ConversationScenario');
  const tCommon = useTranslations('Common');
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

  const [categories, setCategories] = useState<ConversationCategory[]>(Categories());

  // Reset form state when component mounts
  useEffect(() => {
    reset();
  }, [reset]);

  useEffect(() => {
    setCategories((prev) =>
      prev.map((cat) => {
        const match = categoriesData.find((f: ConversationCategory) => f.id === cat.id);
        return match ? { ...cat, defaultContext: match.defaultContext } : cat;
      })
    );
  }, [categoriesData]);

  const isStepValid = (step: number): boolean => {
    switch (step) {
      case 0:
        return !!formState.category;
      case 1:
        return !!formState.difficulty && !!formState.persona;
      default:
        return false;
    }
  };

  const submitForm = async () => {
    if (currentStep !== 1) {
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
      tone: '',
      languageCode: locale as string,
    };

    try {
      const { data } = await conversationScenarioService.createConversationScenario(api, scenario);
      router.push(`/preparation/${data.scenarioId}`);
      setTimeout(reset, 2000);
    } catch (error) {
      showErrorToast(error, t('errorMessage'));
      setIsSubmitting(false);
    }
  };

  const getButtonText = () => {
    if (isSubmitting && currentStep === 1) {
      return t('creating');
    }
    if (currentStep === 1) {
      return t('create');
    }
    return tCommon('next');
  };

  return (
    <div>
      <h1 className="text-2xl text-font-dark text-left w-full mb-8">{t('title')}</h1>

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
        <CustomizeStep
          difficulty={formState.difficulty}
          selectedPersona={formState.persona}
          onDifficultyChange={(val) => updateForm({ difficulty: val })}
          onPersonaSelect={(persona: Persona) => updateForm({ persona: persona.id })}
        />
      )}

      <div className="flex gap-4 w-full justify-center mt-8 mx-auto">
        {currentStep !== 0 && (
          <Button
            size="full"
            variant="outline"
            onClick={() => setStep(currentStep - 1)}
            disabled={currentStep === 0}
          >
            <ArrowLeftIcon />
            {tCommon('back')}
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
