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
} from '@/interfaces/models/ConversationScenario';
import { useConversationScenarioStore } from '@/store/ConversationScenarioStore';
import { api } from '@/services/ApiClient';
import { Categories } from '@/lib/constants/categories';
import Stepper from '@/components/common/Stepper';
import { CategoryStep } from './CategoryStep';
import { CustomizeStep } from './CustomizeStep';

interface ConversationScenarioFormProps {
  categoriesData: ConversationCategory[];
}

interface ContextCardButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  selected: boolean;
  label: string;
  subtitle: string;
  onClick: () => void;
}

function ContextCardButton({
  selected,
  label,
  subtitle,
  onClick,
  ...props
}: ContextCardButtonProps) {
  return (
    <button
      type="button"
      className={`w-full md:w-1/2 box-border rounded-2xl flex flex-col items-start justify-center text-lg outline outline-2 outline-bw-20 cursor-pointer hover:bg-marigold-30/80 active:outline-none active:bg-marigold-30 disabled:pointer-events-none p-6 group ${selected ? 'outline-none bg-marigold-30' : ''}`}
      onClick={onClick}
      {...props}
    >
      <span className="text-xl text-bw-70 font-semibold mb-2 text-left">{label}</span>
      <span
        className={`text-base leading-relaxed text-bw-40 group-hover:text-bw-70 ${selected ? 'text-bw-70' : ''} text-left`}
      >
        {subtitle}
      </span>
    </button>
  );
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

  const contextModes = [
    {
      value: 'default',
      label: tContext('default'),
      subtitle: tContext('defaultSubtitle'),
    },
    {
      value: 'custom',
      label: tContext('custom'),
      subtitle: tContext('customSubtitle'),
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

  const contextClass = `border border-bw-40 placeholder:text-muted-foreground flex field-sizing-content w-full rounded-md bg-white px-3 py-2 text-base shadow-xs transition-[color,box-shadow] outline-none ${formState.contextMode === 'custom' ? '' : 'text-bw-60 cursor-not-allowed'} resize-none overflow-auto`;

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
        <>
          <h2 className="text-xl font-semibold text-center w-full mb-8">
            {t('customizationTitle')}
          </h2>
          <div className="mb-10 w-full flex flex-col sm:flex-row gap-4">
            {contextModes.map((option) => (
              <ContextCardButton
                key={option.value}
                selected={formState.contextMode === option.value}
                label={option.label}
                subtitle={option.subtitle}
                onClick={() => updateForm({ contextMode: option.value as 'default' | 'custom' })}
              />
            ))}
          </div>
        </>
      )}

      {currentStep === 1 && (
        <>
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
          <div className="mt-8 mb-8">
            <div className="mb-4 font-medium text-xl">{t('selectContext')}</div>
            <textarea
              className={contextClass}
              value={formState.situationalFacts}
              onChange={
                formState.contextMode === 'custom'
                  ? (e) => {
                      updateForm({ situationalFacts: e.target.value });
                    }
                  : undefined
              }
              placeholder={t('situation.context.placeholder')}
              rows={16}
              readOnly={formState.contextMode !== 'custom'}
              disabled={formState.contextMode !== 'custom'}
            />
          </div>
        </>
      )}

      {currentStep === 2 && (
        <>
          <h2 className="text-xl font-semibold text-center w-full mb-8">{t('chooseOtherParty')}</h2>
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
        </>
      )}

      <div className="fixed bottom-0 left-0 w-full z-50 bg-white/95 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-[clamp(1.25rem,4vw,4rem)] py-6 flex gap-4 justify-center shadow-2xl">
          {currentStep === 0 && (
            <Button
              size="full"
              onClick={() => setStep(currentStep + 1)}
              variant={!isStepValid(currentStep) ? 'disabled' : 'default'}
              disabled={!isStepValid(currentStep)}
            >
              {tCommon('next')}
              <ArrowRightIcon />
            </Button>
          )}
          {currentStep === 1 && (
            <>
              <Button size="full" variant="outline" onClick={() => setStep(currentStep - 1)}>
                <ArrowLeftIcon />
                {tCommon('back')}
              </Button>
              <Button
                size="full"
                onClick={() => setStep(currentStep + 1)}
                variant={!isStepValid(currentStep) ? 'disabled' : 'default'}
                disabled={!isStepValid(currentStep)}
              >
                {tCommon('next')}
                <ArrowRightIcon />
              </Button>
            </>
          )}
          {currentStep === 2 && (
            <>
              <Button size="full" variant="outline" onClick={() => setStep(currentStep - 1)}>
                <ArrowLeftIcon />
                {tCommon('back')}
              </Button>
              <Button
                size="full"
                onClick={submitForm}
                variant={isSubmitting || !isStepValid(currentStep) ? 'disabled' : 'default'}
                disabled={isSubmitting || !isStepValid(currentStep)}
              >
                {t('create')}
                <ArrowRightIcon />
              </Button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
