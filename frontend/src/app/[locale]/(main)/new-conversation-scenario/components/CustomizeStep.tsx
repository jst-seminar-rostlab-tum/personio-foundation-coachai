import Image from 'next/image';
import { RadioGroup, RadioGroupItem } from '@/components/ui/RadioGroup';
import { useTranslations } from 'next-intl';
import { CustomizeStepProps } from '@/interfaces/CustomizeStepProps';
import { Persona } from '@/interfaces/Persona';
import { PersonaButton } from './PersonaButton';
import { PersonaInfo } from './PersonaInfo';

export function CustomizeStep({
  difficulty,
  complexity,
  selectedPersona,
  onDifficultyChange,
  onComplexityChange,
  onPersonaSelect,
}: CustomizeStepProps) {
  const t = useTranslations('ConversationScenario.customize');

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
      <div className="text-xl text-font-dark text-left mb-2">{t('persona.title')}</div>
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

      <div className="text-xl text-font-dark text-left mb-2">{t('difficulty.title')}</div>
      <RadioGroup
        value={difficulty}
        onValueChange={onDifficultyChange}
        className="mb-16 flex flex-row justify-between gap-4"
      >
        <label htmlFor="d1" className="flex flex-col items-center space-y-2 cursor-pointer">
          <Image
            src="/icons/difficulty-easy.svg"
            alt={t('difficulty.options.easy')}
            width={56}
            height={56}
          />
          <span className="text-sm">{t('difficulty.options.easy')}</span>
          <RadioGroupItem value="easy" id="d1" />
        </label>
        <label htmlFor="d2" className="flex flex-col items-center space-y-2 cursor-pointer">
          <Image
            src="/icons/difficulty-medium.svg"
            alt={t('difficulty.options.medium')}
            width={56}
            height={56}
          />
          <span className="text-sm">{t('difficulty.options.medium')}</span>
          <RadioGroupItem value="medium" id="d2" />
        </label>
        <label htmlFor="d3" className="flex flex-col items-center space-y-2 cursor-pointer">
          <Image
            src="/icons/difficulty-hard.svg"
            alt={t('difficulty.options.hard')}
            width={56}
            height={56}
          />
          <span className="text-sm">{t('difficulty.options.hard')}</span>
          <RadioGroupItem value="hard" id="d3" />
        </label>
      </RadioGroup>

      <div className="text-xl text-font-dark text-left mb-2">{t('complexity.title')}</div>
      <RadioGroup
        value={complexity}
        onValueChange={onComplexityChange}
        className="mb-8 flex flex-row justify-between gap-4"
      >
        <label htmlFor="c1" className="flex flex-col items-center space-y-2 cursor-pointer">
          <Image
            src="/icons/complexity-simple.svg"
            alt={t('complexity.options.simple')}
            width={56}
            height={56}
          />
          <span className="text-sm">{t('complexity.options.simple')}</span>
          <RadioGroupItem value="simple" id="c1" />
        </label>
        <label htmlFor="c2" className="flex flex-col items-center space-y-2 cursor-pointer">
          <Image
            src="/icons/complexity-medium.svg"
            alt={t('complexity.options.medium')}
            width={56}
            height={56}
          />
          <span className="text-sm">{t('complexity.options.medium')}</span>
          <RadioGroupItem value="medium" id="c2" />
        </label>
        <label htmlFor="c3" className="flex flex-col items-center space-y-2 cursor-pointer">
          <Image
            src="/icons/complexity-complex.svg"
            alt={t('complexity.options.complex')}
            width={56}
            height={56}
          />
          <span className="text-sm">{t('complexity.options.complex')}</span>
          <RadioGroupItem value="complex" id="c3" />
        </label>
      </RadioGroup>
    </div>
  );
}
