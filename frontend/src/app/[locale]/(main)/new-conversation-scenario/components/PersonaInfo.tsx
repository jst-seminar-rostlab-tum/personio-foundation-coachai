import { useTranslations } from 'next-intl';
import { ContextMode, Persona } from '@/interfaces/models/ConversationScenario';
import { useEffect, useState, useCallback } from 'react';

interface PersonaInfoProps {
  selectedPersona: string;
  personas: Persona[];
  contextMode: ContextMode;
  onPersonaDescriptionChange: (description: string) => void;
}

export function PersonaInfo({
  selectedPersona,
  personas,
  contextMode,
  onPersonaDescriptionChange,
}: PersonaInfoProps) {
  const t = useTranslations('ConversationScenario.customize.persona');
  const tAbout = useTranslations('ConversationScenario.customize.persona.about');

  const getPersonaData = (personaId: string) => {
    if (!personaId || personaId.trim() === '')
      return { traits: [], trainingFocus: [], personality: '' };
    try {
      const traits = t.raw(`personas.${personaId}.traits`) as string[];
      const trainingFocus = t.raw(`personas.${personaId}.trainingFocus`) as string[];
      const personality = t.raw(`personas.${personaId}.personality`) as string;
      return { traits, trainingFocus, personality };
    } catch {
      return { traits: [], trainingFocus: [], personality: '' };
    }
  };

  const selectedPersonaData: { traits: string[]; trainingFocus: string[]; personality?: string } =
    getPersonaData(selectedPersona);
  const personaName = personas.find((p) => p.id === selectedPersona)?.name || selectedPersona;

  const renderBullets = useCallback((textOrArray: string[] | string | undefined) => {
    if (Array.isArray(textOrArray)) {
      return textOrArray.map((item) => `• ${item}`).join('\n');
    }
    if (typeof textOrArray === 'string') {
      return textOrArray
        .split(',')
        .map((s) => `• ${s.trim()}`)
        .join('\n');
    }
    return '';
  }, []);

  const [traitsText, setTraitsText] = useState(() => renderBullets(selectedPersonaData.traits));
  const [focusText, setFocusText] = useState(() =>
    renderBullets(selectedPersonaData.trainingFocus)
  );
  const [personalityText, setPersonalityText] = useState(() =>
    renderBullets(selectedPersonaData?.personality || personaName)
  );

  const generateDescription = useCallback(() => {
    let currentPersonality = '';
    let currentTraits = '';
    let currentFocus = '';

    if (contextMode === 'default') {
      currentPersonality = renderBullets(selectedPersonaData?.personality || personaName);
      currentTraits = renderBullets(selectedPersonaData.traits);
      currentFocus = renderBullets(selectedPersonaData.trainingFocus);
    } else {
      currentPersonality = personalityText;
      currentTraits = traitsText;
      currentFocus = focusText;
    }

    let newDescription = '';
    newDescription += `${tAbout('personality')}:\n ${currentPersonality}\n\n`;
    newDescription += `${t('behavioralTraits')}:\n ${currentTraits}\n\n`;
    newDescription += `${t('trainingFocus')}:\n ${currentFocus}`;
    return newDescription;
  }, [
    contextMode,
    selectedPersonaData,
    personaName,
    personalityText,
    traitsText,
    focusText,
    renderBullets,
    tAbout,
    t,
  ]);

  useEffect(() => {
    setTraitsText(renderBullets(selectedPersonaData.traits));
    setFocusText(renderBullets(selectedPersonaData.trainingFocus));
    setPersonalityText(renderBullets(selectedPersonaData?.personality || personaName));

    onPersonaDescriptionChange(generateDescription());
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedPersona, contextMode]);

  useEffect(() => {
    if (contextMode === 'custom') {
      onPersonaDescriptionChange(generateDescription());
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [traitsText, focusText, personalityText, contextMode]);

  const lockedClasses = `border border-bw-40 placeholder:text-muted-foreground flex field-sizing-content w-full rounded-md bg-white px-3 py-2 text-base shadow-xs transition-[color,box-shadow] outline-none ${contextMode === 'custom' ? '' : 'text-bw-60 cursor-not-allowed'} resize-none overflow-auto`;

  if (!selectedPersona || selectedPersona.trim() === '' || !selectedPersonaData.traits.length) {
    return null;
  }

  return (
    <div className="mb-12 border border-bw-20 rounded-2xl p-6">
      <div className="text-xl text-font-dark text-left mb-8">
        {t('aboutLabel')}: {personaName}
      </div>
      <div className="mb-6">
        <label className="mb-2 font-medium text-lg block">{tAbout('personality')}</label>
        <textarea
          className={lockedClasses}
          value={
            contextMode === 'default'
              ? renderBullets(selectedPersonaData?.personality || personaName)
              : personalityText
          }
          onChange={(event) => {
            if (contextMode === 'custom') {
              setPersonalityText(event.target.value);
            }
          }}
          disabled={contextMode === 'default'}
          rows={5}
          style={{ resize: 'none' }}
        />
      </div>
      <div className="flex flex-col sm:flex-row gap-6 items-start justify-center">
        <div className="w-full sm:flex-1 min-w-0">
          <label className="mb-2 font-medium text-lg block">{t('behavioralTraits')}</label>
          <textarea
            className={`${lockedClasses} resize-none`}
            value={
              contextMode === 'default' ? renderBullets(selectedPersonaData.traits) : traitsText
            }
            onChange={(event) => {
              if (contextMode === 'custom') {
                setTraitsText(event.target.value);
              }
            }}
            rows={5}
            disabled={contextMode === 'default'}
          />
        </div>
        <div className="w-full sm:flex-1 min-w-0">
          <label className="mb-2 font-medium text-lg block">{t('trainingFocus')}</label>
          <textarea
            className={`${lockedClasses} resize-none`}
            value={
              contextMode === 'default'
                ? renderBullets(selectedPersonaData.trainingFocus)
                : focusText
            }
            onChange={(event) => {
              if (contextMode === 'custom') {
                setFocusText(event.target.value);
              }
            }}
            rows={5}
            disabled={contextMode === 'default'}
          />
        </div>
      </div>
    </div>
  );
}
