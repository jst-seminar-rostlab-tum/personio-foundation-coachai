import { useTranslations } from 'next-intl';
import { useConversationScenarioStore } from '@/store/ConversationScenarioStore';
import { ContextModeEnums } from '@/interfaces/models/ConversationScenario';
import { useEffect, useState, useCallback, useMemo } from 'react';
import { PersonaTextarea } from './PersonaTextarea';

export function PersonaInfo() {
  const { formState, updateForm } = useConversationScenarioStore();
  const t = useTranslations('ConversationScenario.customize.persona');
  const { contextMode, persona } = formState;
  const isCustomContextMode = contextMode === ContextModeEnums.CUSTOM;

  const getPersonaData = (personaId: string) => {
    if (!personaId || personaId.trim() === '')
      return { traits: [], trainingFocus: [], personality: [] };

    const traits = t.raw(`personas.${personaId}.traits`) as string[];
    const trainingFocus = t.raw(`personas.${personaId}.trainingFocus`) as string[];
    const personality = t.raw(`personas.${personaId}.personality`) as string[];
    return { traits, trainingFocus, personality };
  };

  const selectedPersonaData = getPersonaData(persona);
  const personaName = t.raw(`personas.${persona}.name`) as string;

  const renderBullets = useCallback((textArray?: string[]) => {
    if (!textArray || textArray.length === 0) return '';
    return textArray.map((s) => `- ${s.trim()}`).join('\n');
  }, []);

  const initialTexts = useMemo(
    () => ({
      traits: renderBullets(selectedPersonaData.traits),
      focus: renderBullets(selectedPersonaData.trainingFocus),
      personality: renderBullets(selectedPersonaData.personality),
    }),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [
      selectedPersonaData.traits,
      selectedPersonaData.trainingFocus,
      selectedPersonaData.personality,
      personaName,
      renderBullets,
    ]
  );

  const [texts, setTexts] = useState(initialTexts);

  const generateDescription = useCallback(
    (textData: typeof texts) => {
      return `${t('about.personality')}:\n ${textData.personality}\n\n${t('about.behavioralTraits')}:\n ${textData.traits}\n\n${t('about.trainingFocus')}:\n ${textData.focus}`;
    },
    [t]
  );

  useEffect(() => {
    setTexts(initialTexts);
  }, [initialTexts]);

  useEffect(() => {
    if (isCustomContextMode && generateDescription(texts) !== formState.personaDescription) {
      updateForm({ personaDescription: generateDescription(texts) });
    } else if (
      !isCustomContextMode &&
      formState.personaDescription !== generateDescription(initialTexts)
    ) {
      updateForm({ personaDescription: generateDescription(initialTexts) });
    }
  }, [
    texts,
    isCustomContextMode,
    generateDescription,
    initialTexts,
    updateForm,
    formState.personaDescription,
  ]);

  if (!persona || persona.trim() === '' || !selectedPersonaData.traits.length) {
    return null;
  }

  return (
    <div className="mb-12 border border-bw-20 rounded-2xl p-6">
      <div className="text-xl text-font-dark text-left mb-8">
        {t('aboutLabel')}: {personaName}
      </div>

      <div className="mb-6">
        <PersonaTextarea
          label={t('about.personality')}
          value={isCustomContextMode ? texts.personality : initialTexts.personality}
          onChange={(val: string) => setTexts((prev) => ({ ...prev, personality: val }))}
          isCustomContextMode={isCustomContextMode}
        />
      </div>

      <div className="flex flex-col sm:flex-row gap-6 items-start justify-center">
        <PersonaTextarea
          label={t('about.behavioralTraits')}
          value={isCustomContextMode ? texts.traits : initialTexts.traits}
          onChange={(val: string) => setTexts((prev) => ({ ...prev, traits: val }))}
          isCustomContextMode={isCustomContextMode}
        />
        <PersonaTextarea
          label={t('about.trainingFocus')}
          value={isCustomContextMode ? texts.focus : initialTexts.focus}
          onChange={(val: string) => setTexts((prev) => ({ ...prev, focus: val }))}
          isCustomContextMode={isCustomContextMode}
        />
      </div>
    </div>
  );
}
