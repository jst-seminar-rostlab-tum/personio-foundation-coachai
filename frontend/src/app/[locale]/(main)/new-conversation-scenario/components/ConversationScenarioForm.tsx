'use client';

import { Button } from '@/components/ui/Button';
import { ArrowLeftIcon, ArrowRightIcon } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
import { useParams, useRouter } from 'next/navigation';
import { conversationScenarioService } from '@/services/ConversationScenarioService';
import { showErrorToast } from '@/lib/utils/toast';
import {
  ConversationScenario,
  ConversationCategory,
  Persona,
  ContextMode,
} from '@/interfaces/models/ConversationScenario';
import { useConversationScenarioStore } from '@/store/ConversationScenarioStore';
import { api } from '@/services/ApiClient';
import { Categories } from '@/lib/constants/categories';
import Stepper from '@/components/common/Stepper';
import { CategoryStep } from './CategoryStep';
import { CustomizeStep } from './CustomizeStep';
import ContextCardButton from './ContextCardButton';

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

  const contextModes = [
    {
      value: 'default',
      label: t('customize.context.default'),
      subtitle: t('customize.context.defaultSubtitle'),
    },
    {
      value: 'custom',
      label: t('customize.context.custom'),
      subtitle: t('customize.context.customSubtitle'),
    },
  ];

  useEffect(() => {
    setCategories((prev) =>
      prev.map((cat) => {
        const match = categoriesData.find((f: ConversationCategory) => f.id === cat.id);
        return match ? { ...cat, defaultContext: match.defaultContext } : cat;
      })
    );
  }, [categoriesData]);

  const selectedCategoryObj = categories.find((cat) => cat.id === formState.category);
  const selectedCategoryKey = Object.entries(t.raw('categories')).find(
    ([, val]) => (val as { name: string }).name === selectedCategoryObj?.name
  )?.[0];

  const defaultContextLong = selectedCategoryKey
    ? t(`categories.${selectedCategoryKey}.defaultContextLong`)
    : '';

  useEffect(() => {
    if (defaultContextLong) {
      updateForm({ situationalFacts: defaultContextLong });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [formState.category, formState.contextMode, defaultContextLong]);

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
      customCategoryLabel: formState.customCategory,
      difficultyLevel: formState.difficulty,
      persona: formState.personaDescription,
      situationalFacts: formState.situationalFacts,
      languageCode: locale as string,
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
        steps={[t('contextDefault'), t('category.title'), t('chooseOtherParty')]}
        currentStep={currentStep}
        showAllStepNumbers={true}
        showStepLabels={false}
        className="mb-8 md:w-3/4 mx-auto"
      />

      {currentStep === 0 && (
        <div className="mb-10 w-full flex flex-col sm:flex-row gap-4">
          {contextModes.map((option) => (
            <ContextCardButton
              key={option.value}
              selected={formState.contextMode === option.value}
              label={option.label}
              subtitle={option.subtitle}
              onClick={() => updateForm({ contextMode: option.value as ContextMode })}
            />
          ))}
        </div>
      )}

      {currentStep === 1 && (
        <CategoryStep
          selectedCategory={formState.category}
          onCategorySelect={(category) =>
            updateForm({
              category: category.id,
              name: category.name,
              situationalFacts: formState.situationalFacts,
            })
          }
          categories={categories}
        />
      )}

      {currentStep === 2 && (
        <CustomizeStep
          difficulty={formState.difficulty}
          selectedPersona={formState.persona}
          contextMode={formState.contextMode}
          onDifficultyChange={(val) => updateForm({ difficulty: val })}
          onPersonaSelect={(persona: Persona) => updateForm({ persona: persona.id })}
          onPersonaDescriptionChange={(description: string) =>
            updateForm({ personaDescription: description })
          }
        />
      )}

      <div className="fixed bottom-0 left-0 w-full z-50 bg-white/95 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-[clamp(1.25rem,4vw,4rem)] py-6 flex gap-4 justify-center shadow-2xl">
          {currentStep > 0 && (
            <Button size="full" variant="outline" onClick={() => setStep(currentStep - 1)}>
              <ArrowLeftIcon />
              {tCommon('back')}
            </Button>
          )}
          {
            <Button
              size="full"
              onClick={currentStep < 2 ? () => setStep(currentStep + 1) : submitForm}
              variant={isSubmitting || !isStepValid(currentStep) ? 'disabled' : 'default'}
              disabled={isSubmitting || !isStepValid(currentStep)}
            >
              {currentStep < 2 ? tCommon('next') : t('create')}
              <ArrowRightIcon />
            </Button>
          }
        </div>
      </div>
    </div>
  );
}
