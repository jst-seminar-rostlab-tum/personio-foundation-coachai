import Image from 'next/image';
import { RadioGroup, RadioGroupItem } from '@/components/ui/RadioGroup';
import { useTranslations } from 'next-intl';
import { CustomizeStepProps } from '@/interfaces/CustomizeStepProps';
import { Persona } from '@/interfaces/Persona';
import { PersonaButton } from './PersonaButton';
import { PersonaInfo } from './PersonaInfo';

export function CustomizeStep({
  difficulty,
  selectedPersona,
  onDifficultyChange,
  onPersonaSelect,
}: CustomizeStepProps) {
  const t = useTranslations('ConversationScenario');

  const personas: Persona[] = [
    {
      id: 'positive',
      name: 'Positive Pam',
      imageUri: '/images/personas/persona-positive.png',
    },
    {
      id: 'angry',
      name: 'Angry Alex',
      imageUri: '/images/personas/persona-angry.png',
    },
    {
      id: 'shy',
      name: 'Shy Sarah',
      imageUri: '/images/personas/persona-shy.png',
    },
    {
      id: 'casual',
      name: 'Casual Candice',
      imageUri: '/images/personas/persona-casual.png',
    },
    {
      id: 'sad',
      name: 'Sad Steve',
      imageUri: '/images/personas/persona-sad.png',
    },
  ];

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
            <div className="relative w-28 h-28 rounded-full overflow-hidden bg-white mb-3 flex-shrink-0">
              <Image src={persona.imageUri} alt={persona.name} fill className="object-cover" />
            </div>
            <span className="text-sm text-center">{persona.name}</span>
          </PersonaButton>
        ))}
      </div>

      {/* Persona Information */}
      <PersonaInfo selectedPersona={selectedPersona} personas={personas} />

      <div className="text-xl text-font-dark text-left mb-2">{t('difficultyTitle')}</div>
      <RadioGroup
        value={difficulty}
        onValueChange={onDifficultyChange}
        className="mb-16 flex flex-row justify-between gap-4"
      >
        <label htmlFor="d1" className="flex flex-col items-center space-y-2 cursor-pointer">
          <Image src="/images/difficulty/easy.svg" alt={t('easy')} width={56} height={56} />
          <span className="text-sm">{t('easy')}</span>
          <RadioGroupItem value="easy" id="d1" />
        </label>
        <label htmlFor="d2" className="flex flex-col items-center space-y-2 cursor-pointer">
          <Image src="/images/difficulty/medium.svg" alt={t('medium')} width={56} height={56} />
          <span className="text-sm">{t('medium')}</span>
          <RadioGroupItem value="medium" id="d2" />
        </label>
        <label htmlFor="d3" className="flex flex-col items-center space-y-2 cursor-pointer">
          <Image src="/images/difficulty/hard.svg" alt={t('hard')} width={56} height={56} />
          <span className="text-sm">{t('hard')}</span>
          <RadioGroupItem value="hard" id="d3" />
        </label>
      </RadioGroup>
    </div>
  );
}
