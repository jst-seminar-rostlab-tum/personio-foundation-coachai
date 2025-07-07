import { useTranslations } from 'next-intl';
import { Persona } from '@/interfaces/Persona';
import { useState } from 'react';
import { useConversationScenarioStore } from '@/store/ConversationScenarioStore';

interface PersonaInfoProps {
  selectedPersona: string;
  personas: Persona[];
}

export function PersonaInfo({ selectedPersona, personas }: PersonaInfoProps) {
  const t = useTranslations('ConversationScenario.customize.persona');
  const tAbout = useTranslations('ConversationScenario.customize.persona.about');
  const { contextMode } = useConversationScenarioStore();

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
  const [traitsText, setTraitsText] = useState(selectedPersonaData.traits.join('\n'));
  const [focusText, setFocusText] = useState(selectedPersonaData.trainingFocus.join('\n'));
  const [personalityText, setPersonalityText] = useState(
    renderBullets(selectedPersonaData?.personality || personaName)
  );

  // Shared style for locked/disabled state (matches context Textarea)
  const lockedClasses =
    'border border-bw-40 placeholder:text-muted-foreground flex field-sizing-content h-[120px] w-full rounded-md bg-transparent px-3 py-2 text-base shadow-xs transition-[color,box-shadow] outline-none focus:outline-none focus:ring-2 focus:ring-bw-40 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50';

  // Helper to render bullet points for locked fields
  function renderBullets(textOrArray: string[] | string | undefined) {
    if (Array.isArray(textOrArray)) {
      return textOrArray.map((item) => `• ${item}`).join('\n');
    }
    if (typeof textOrArray === 'string') {
      // Split comma-separated string for personality
      return textOrArray
        .split(',')
        .map((s) => `• ${s.trim()}`)
        .join('\n');
    }
    return '';
  }

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
            if (contextMode === 'custom') setPersonalityText(event.target.value);
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
              if (contextMode === 'custom') setTraitsText(event.target.value);
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
