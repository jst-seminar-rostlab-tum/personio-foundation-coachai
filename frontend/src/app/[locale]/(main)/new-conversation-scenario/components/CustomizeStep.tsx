import Image from 'next/image';
import { useTranslations } from 'next-intl';
import { CustomizeStepProps } from '@/interfaces/CustomizeStepProps';
import { PersonaButton } from './PersonaButton';
import { PersonaInfo } from './PersonaInfo';

export function CustomizeStep({
  difficulty,
  selectedPersona,
  onDifficultyChange,
  onPersonaSelect,
}: CustomizeStepProps) {
  const t = useTranslations('ConversationScenario');

  const personaKeys = ['positive', 'angry', 'shy', 'casual', 'sad'];
  const personas = personaKeys.map((key) => ({
    id: key,
    name: t(`customize.persona.personas.${key}.name`),
    imageUri: t.raw(`customize.persona.personas.${key}.imageUri`),
  }));

  return (
    <div>
      <div className="text-xl text-font-dark text-center w-full mb-8">{t('title')}</div>

      {/* Persona Selection */}
      <div className="text-xl text-font-dark text-left mb-2">{t('personaSelection')}</div>
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4 w-full mx-auto mb-16">
        {personas.map((persona) => (
          <PersonaButton
            key={persona.id}
            onClick={() => onPersonaSelect(persona)}
            selected={selectedPersona === persona.id}
            className="w-full"
          >
            <div className="relative w-20 h-20 sm:w-28 sm:h-28 rounded-full overflow-hidden bg-white mb-3 flex-shrink-0">
              <Image src={persona.imageUri} alt={persona.name} fill className="object-cover" />
            </div>
            <span className="text-sm text-center">{persona.name}</span>
          </PersonaButton>
        ))}
      </div>

      {/* Persona Information */}
      <PersonaInfo selectedPersona={selectedPersona} personas={personas} />

      <div className="text-xl text-font-dark text-left mb-2">{t('difficultyTitle')}</div>
      <div className="mb-16 grid grid-cols-3 gap-4 w-full mx-auto">
        {[
          { value: 'easy', icon: '/images/difficulty/easy.svg', label: t('easy') },
          { value: 'medium', icon: '/images/difficulty/medium.svg', label: t('medium') },
          { value: 'hard', icon: '/images/difficulty/hard.svg', label: t('hard') },
        ].map((diff) => (
          <PersonaButton
            key={diff.value}
            onClick={() => onDifficultyChange(diff.value)}
            selected={difficulty === diff.value}
            className="w-full"
          >
            <div className="relative w-10 h-10 sm:w-16 sm:h-16 rounded-full overflow-hidden bg-white mb-3 flex-shrink-0 mx-auto">
              <Image src={diff.icon} alt={diff.label} fill className="object-contain" />
            </div>
            <span className="text-sm text-center">{diff.label}</span>
          </PersonaButton>
        ))}
      </div>
    </div>
  );
}
