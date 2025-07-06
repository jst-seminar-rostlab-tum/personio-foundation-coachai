import { useTranslations } from 'next-intl';
import { Persona } from '@/interfaces/Persona';
import { useState, useRef, useEffect } from 'react';
import { useConversationScenarioStore } from '@/store/ConversationScenarioStore';

interface PersonaInfoProps {
  selectedPersona: string;
  personas: Persona[];
}

export function PersonaInfo({ selectedPersona, personas }: PersonaInfoProps) {
  const t = useTranslations('ConversationScenario.customize.persona');
  const { contextMode } = useConversationScenarioStore();

  const getPersonaData = (personaId: string) => {
    if (!personaId || personaId.trim() === '') return { traits: [], trainingFocus: [] };
    try {
      const traits = t.raw(`personas.${personaId}.traits`) as string[];
      const trainingFocus = t.raw(`personas.${personaId}.trainingFocus`) as string[];
      return { traits, trainingFocus };
    } catch {
      return { traits: [], trainingFocus: [] };
    }
  };

  const selectedPersonaData = getPersonaData(selectedPersona);
  const personaName = personas.find((p) => p.id === selectedPersona)?.name || selectedPersona;
  const [traitsText, setTraitsText] = useState(selectedPersonaData.traits.join('\n'));
  const [focusText, setFocusText] = useState(selectedPersonaData.trainingFocus.join('\n'));
  const [personalityText, setPersonalityText] = useState(personaName);
  const traitsRef = useRef<HTMLTextAreaElement>(null);
  const focusRef = useRef<HTMLTextAreaElement>(null);

  // Shared style for locked/disabled state (matches context Textarea)
  const lockedClasses =
    'border border-bw-40 placeholder:text-muted-foreground flex field-sizing-content min-h-16 w-full rounded-md bg-transparent px-3 py-2 text-base shadow-xs transition-[color,box-shadow] outline-none focus:outline-none focus:ring-2 focus:ring-bw-40 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50';

  useEffect(() => {
    if (traitsRef.current && focusRef.current) {
      traitsRef.current.style.height = 'auto';
      focusRef.current.style.height = 'auto';
      const traitsHeight = traitsRef.current.scrollHeight;
      const focusHeight = focusRef.current.scrollHeight;
      const maxHeight = Math.max(traitsHeight, focusHeight);
      traitsRef.current.style.height = `${maxHeight}px`;
      focusRef.current.style.height = `${maxHeight}px`;
    }
  }, [traitsText, focusText]);

  if (!selectedPersona || selectedPersona.trim() === '' || !selectedPersonaData.traits.length) {
    return null;
  }

  return (
    <div className="mb-12 border border-bw-20 rounded-2xl p-6">
      <div className="text-xl text-font-dark text-left mb-8">
        {t('about')}: {personaName}
      </div>
      <div className="mb-6">
        <label className="mb-2 font-medium text-lg block">Personality</label>
        <input
          type="text"
          className={lockedClasses}
          value={contextMode === 'default' ? personaName : personalityText}
          onChange={(event) => {
            if (contextMode === 'custom') setPersonalityText(event.target.value);
          }}
          disabled={contextMode === 'default'}
        />
      </div>
      <div className="flex flex-col sm:flex-row gap-6 items-start justify-center">
        <div className="w-full sm:flex-1 min-w-0">
          <label className="mb-2 font-medium text-lg block">{t('behavioralTraits')}</label>
          <textarea
            ref={traitsRef}
            className={lockedClasses}
            value={contextMode === 'default' ? selectedPersonaData.traits.join('\n') : traitsText}
            onChange={(event) => {
              if (contextMode === 'custom') setTraitsText(event.target.value);
            }}
            rows={5}
            disabled={contextMode === 'default'}
          />
        </div>
        <div className="w-full sm:flex-1 min-w-0">
          <label className="mb-2 font-medium text-lg block">{t('trainingFocus')}</label>
          <textarea
            ref={focusRef}
            className={lockedClasses}
            value={
              contextMode === 'default' ? selectedPersonaData.trainingFocus.join('\n') : focusText
            }
            onChange={(event) => {
              if (contextMode === 'custom') setFocusText(event.target.value);
            }}
            rows={5}
            disabled={contextMode === 'default'}
          />
        </div>
      </div>
    </div>
  );
}
