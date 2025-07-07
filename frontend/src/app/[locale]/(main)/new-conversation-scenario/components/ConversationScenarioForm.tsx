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
import { Textarea } from '@/components/ui/Textarea';
import { RadioGroup, RadioGroupItem } from '@/components/ui/RadioGroup';
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
  const tContext = useTranslations('ConversationScenario.customize.context');
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
  const { contextMode, setContextMode, customContext, setCustomContext } =
    useConversationScenarioStore();

  const contextCardBase =
    'w-full box-border rounded-md flex flex-row items-center text-lg outline outline-2 outline-bw-20 cursor-pointer hover:bg-marigold-30/80 active:outline-none active:bg-marigold-30 disabled:pointer-events-none p-4 text-left gap-3';

  useEffect(() => {
    setCategories((prev) =>
      prev.map((cat) => {
        const match = categoriesData.find((f: ConversationCategory) => f.id === cat.id);
        return match ? { ...cat, defaultContext: match.defaultContext } : cat;
      })
    );
  }, [categoriesData]);

  // Find the selected category object and key
  const selectedCategoryObj = categories.find((cat) => cat.id === formState.category);
  const selectedCategoryKey = Object.entries(t.raw('categories')).find(
    ([, val]) => (val as { name: string }).name === selectedCategoryObj?.name
  )?.[0];

  // Use translation-based long default context
  const defaultContextLong = selectedCategoryKey
    ? t(`categories.${selectedCategoryKey}.defaultContextLong`)
    : '';

  // When scenario changes, if contextMode is 'default', update context in form state
  useEffect(() => {
    if (contextMode === 'default' && defaultContextLong) {
      // Do not overwrite customContext
      updateForm({ context: defaultContextLong });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [formState.category, contextMode, defaultContextLong]);

  // When switching to custom, restore the last customContext
  useEffect(() => {
    if (contextMode === 'custom') {
      updateForm({ context: customContext });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [contextMode, customContext]);

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
      context: contextMode === 'custom' ? customContext : defaultContextLong,
      goal: formState.goal,
      otherParty: formState.otherParty,
      difficultyLevel: formState.difficulty,
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
              context: contextMode === 'default' ? defaultContextLong : customContext,
              goal: category.defaultGoal || '',
              otherParty: category.defaultOtherParty || '',
              isCustom: category.isCustom || false,
            })
          }
          categories={categories}
        />
      )}

      {currentStep === 1 && (
        <>
          {/* Context Selection Section */}
          <div className="mb-10">
            <RadioGroup
              value={contextMode}
              onValueChange={(val) => setContextMode(val as 'default' | 'custom')}
              className="flex gap-4 mb-4"
            >
              {[
                { value: 'default', label: tContext('default') },
                { value: 'custom', label: tContext('custom') },
              ].map((option) => (
                <label
                  key={option.value}
                  className={`${
                    contextCardBase + (contextMode === option.value ? ' bg-marigold-30' : '')
                  } select-none`}
                  style={{ outline: contextMode === option.value ? 'none' : undefined }}
                >
                  <RadioGroupItem
                    value={option.value}
                    className="mr-3 bg-white border border-bw-40 data-[state=checked]:border-bw-70 size-4"
                  >
                    <span className="block w-2 h-2 rounded-full bg-bw-70" />
                  </RadioGroupItem>
                  <span className="text-base font-medium">{option.label}</span>
                </label>
              ))}
            </RadioGroup>
            <div className="mt-12 mb-4 font-medium text-xl">{t('selectContext')}</div>
            <Textarea
              className="w-full min-h-32 text-base"
              value={contextMode === 'default' ? defaultContextLong : customContext}
              onChange={(e) => {
                if (contextMode === 'custom') {
                  setCustomContext(e.target.value);
                  updateForm({ context: e.target.value });
                }
              }}
              disabled={contextMode === 'default'}
              placeholder="Enter the context for your scenario..."
            />
          </div>
          <CustomizeStep
            difficulty={formState.difficulty}
            selectedPersona={formState.persona}
            onDifficultyChange={(val) => updateForm({ difficulty: val })}
            onPersonaSelect={(persona: Persona) => updateForm({ persona: persona.id })}
          />
        </>
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
