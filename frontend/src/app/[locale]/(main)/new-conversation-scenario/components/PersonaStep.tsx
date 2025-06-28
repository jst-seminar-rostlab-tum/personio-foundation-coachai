'use client';

import { useTranslations } from 'next-intl';
import Image from 'next/image';
import { PersonaStepProps } from '@/interfaces/PersonaStepProps';
import { PersonaButton } from './PersonaButton';

export function PersonaStep({ selectedPersona, onPersonaSelect, personas }: PersonaStepProps) {
  const t = useTranslations('ConversationScenario.persona');
  return (
    <div className="space-y-8">
      <div className="text-xl text-font-dark text-center">{t('title')}</div>
      <div className="flex flex-row justify-between gap-4 w-full mx-auto">
        {personas.map((persona) => (
          <PersonaButton
            key={persona.id}
            onClick={() => onPersonaSelect(persona)}
            selected={selectedPersona === persona.id}
            className="flex-1"
          >
            <div className="relative w-20 h-20 rounded-full overflow-hidden border-2 border-bw-20 bg-white mb-3 flex-shrink-0">
              <Image src={persona.imageUri} alt={persona.name} fill className="object-cover" />
            </div>
            <span className="text-sm text-center">{persona.name}</span>
          </PersonaButton>
        ))}
      </div>
    </div>
  );
}
