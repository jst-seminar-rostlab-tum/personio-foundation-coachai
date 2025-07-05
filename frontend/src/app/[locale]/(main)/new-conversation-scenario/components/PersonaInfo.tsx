import { useTranslations } from 'next-intl';
import { Persona } from '@/interfaces/Persona';
import { ArrowRightIcon, ArrowDownIcon } from 'lucide-react';

interface PersonaInfoProps {
  selectedPersona: string;
  personas: Persona[];
}

interface PersonaInfoBlockProps {
  title: string;
  items: string[];
}

function PersonaInfoBlock({ title, items }: PersonaInfoBlockProps) {
  return (
    <div className="rounded-lg p-4 w-full sm:flex-1 flex flex-col items-center justify-center">
      <div className="text-lg font-medium text-font-dark mb-3 text-center">{title}</div>
      <ul className="space-y-2">
        {items.map((item, index) => (
          <li key={index} className="text-base text-font-dark flex items-start">
            <span className="text-marigold-50 mr-2">•</span>
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}

export function PersonaInfo({ selectedPersona, personas }: PersonaInfoProps) {
  const t = useTranslations('ConversationScenario.customize.persona');

  const getPersonaData = (personaId: string) => {
    // Validate that personaId is not empty
    if (!personaId || personaId.trim() === '') {
      return null;
    }

    try {
      const traits = t.raw(`personas.${personaId}.traits`) as string[];
      const trainingFocus = t.raw(`personas.${personaId}.trainingFocus`) as string[];

      if (traits && trainingFocus && traits.length > 0 && trainingFocus.length > 0) {
        return { traits, trainingFocus };
      }
      return null;
    } catch {
      return null;
    }
  };

  // Don't render if no persona is selected
  if (!selectedPersona || selectedPersona.trim() === '') {
    return null;
  }

  const selectedPersonaData = getPersonaData(selectedPersona);

  if (!selectedPersonaData) {
    return null;
  }

  const personaName = personas.find((p) => p.id === selectedPersona)?.name || selectedPersona;

  return (
    <div className="mb-12 border border-gray-200 rounded-lg p-6">
      <div className="text-xl text-font-dark text-left mb-4">
        {t('about')}: {personaName}
      </div>
      <div className="flex flex-col sm:flex-row gap-6 items-center justify-center">
        <PersonaInfoBlock title={t('behavioralTraits')} items={selectedPersonaData.traits} />
        {/* Arrow connecting the two boxes */}
        <div className="flex justify-center items-center">
          <ArrowDownIcon className="w-8 h-8 text-bw-70 sm:hidden" />
          <ArrowRightIcon className="w-8 h-8 text-bw-70 hidden sm:block" />
        </div>
        <PersonaInfoBlock title={t('trainingFocus')} items={selectedPersonaData.trainingFocus} />
      </div>
    </div>
  );
}
