import { useTranslations } from 'next-intl';
import { DifficultyLevelEnums, PersonaEnums } from '@/interfaces/models/ConversationScenario';
import { useConversationScenarioStore } from '@/store/ConversationScenarioStore';
import { PersonaButton } from './PersonaButton';
import { PersonaInfo } from './PersonaInfo';

/**
 * Renders persona and difficulty selection step.
 */
export function CustomizeStep() {
  const t = useTranslations('ConversationScenario');

  const personaKeys = [
    PersonaEnums.POSITIVE,
    PersonaEnums.ANGRY,
    PersonaEnums.SHY,
    PersonaEnums.CASUAL,
    PersonaEnums.SAD,
  ];

  const { formState, updateForm } = useConversationScenarioStore();

  const personas = personaKeys.map((key) => ({
    id: key,
    name: t(`customize.persona.personas.${key}.name`),
    imageUri: t.raw(`customize.persona.personas.${key}.imageUri`),
  }));

  const difficultyOptions = [
    { value: DifficultyLevelEnums.EASY, icon: '/images/difficulty/easy.svg', label: t('easy') },
    {
      value: DifficultyLevelEnums.MEDIUM,
      icon: '/images/difficulty/medium.svg',
      label: t('medium'),
    },
    { value: DifficultyLevelEnums.HARD, icon: '/images/difficulty/hard.svg', label: t('hard') },
  ];

  return (
    <div>
      <h2 className="text-xl font-semibold text-center w-full mb-8">{t('chooseOtherParty')}</h2>
      <div className="mb-4 font-medium text-xl">{t('personaSelection')}</div>
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-5 w-full mx-auto mb-12">
        {personas.map((persona) => (
          <PersonaButton
            key={persona.id}
            onClick={() => updateForm({ persona: persona.id })}
            selected={formState.persona === persona.id}
            image={persona.imageUri}
            label={persona.name}
          />
        ))}
      </div>

      <PersonaInfo />

      <div className="mb-4 font-medium text-xl">{t('difficultyTitle')}</div>
      <div className="mb-16 grid grid-cols-3 gap-4 w-full mx-auto">
        {difficultyOptions.map((diff) => (
          <PersonaButton
            key={diff.value}
            onClick={() => updateForm({ difficulty: diff.value })}
            selected={formState.difficulty === diff.value}
            image={diff.icon}
            label={diff.label}
          />
        ))}
      </div>
    </div>
  );
}
