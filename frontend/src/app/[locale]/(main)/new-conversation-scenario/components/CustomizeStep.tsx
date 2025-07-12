import Image from 'next/image';
import { useTranslations } from 'next-intl';
import { ContextMode, Persona } from '@/interfaces/models/ConversationScenario';
import { useConversationScenarioStore } from '@/store/ConversationScenarioStore';
import { PersonaButton } from './PersonaButton';
import { PersonaInfo } from './PersonaInfo';

interface CustomizeStepProps {
  difficulty: string;
  selectedPersona: string;
  contextMode: ContextMode;
  onDifficultyChange: (difficulty: string) => void;
  onPersonaSelect: (persona: Persona) => void;
  onPersonaDescriptionChange: (description: string) => void;
}

export function CustomizeStep({
  difficulty,
  selectedPersona,
  contextMode,
  onDifficultyChange,
  onPersonaSelect,
  onPersonaDescriptionChange,
}: CustomizeStepProps) {
  const t = useTranslations('ConversationScenario');
  const { formState, updateForm } = useConversationScenarioStore();
  const personaKeys = ['positive', 'angry', 'shy', 'casual', 'sad'];
  const personas = personaKeys.map((key) => ({
    id: key,
    name: t(`customize.persona.personas.${key}.name`),
    imageUri: t.raw(`customize.persona.personas.${key}.imageUri`),
  }));
  const difficultyOptions = [
    { value: 'easy', icon: '/images/difficulty/easy.svg', label: t('easy') },
    { value: 'medium', icon: '/images/difficulty/medium.svg', label: t('medium') },
    { value: 'hard', icon: '/images/difficulty/hard.svg', label: t('hard') },
  ];
  const isCustomMode = contextMode === 'custom';
  const contextClass = `border border-bw-40 placeholder:text-muted-foreground flex field-sizing-content w-full rounded-md bg-white px-3 py-2 text-base shadow-xs transition-[color,box-shadow] outline-none ${isCustomMode ? '' : 'text-bw-60 cursor-not-allowed'} resize-none overflow-auto`;

  return (
    <div>
      <h2 className="text-xl font-semibold text-center w-full mb-8">{t('chooseOtherParty')}</h2>
      <div className="mb-4 font-medium text-xl">{t('personaSelection')}</div>
      <div className="grid grid-cols-3 gap-4 w-full mx-auto mb-12">
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

      <PersonaInfo
        selectedPersona={selectedPersona}
        personas={personas}
        contextMode={contextMode}
        onPersonaDescriptionChange={onPersonaDescriptionChange}
      />

      <div className="mb-4 font-medium text-xl">{t('difficultyTitle')}</div>
      <div className="mb-16 grid grid-cols-3 gap-4 w-full mx-auto">
        {difficultyOptions.map((diff) => (
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

      <div className="mt-8 mb-8">
        <div className="mb-4 font-medium text-xl">{t('selectContext')}</div>
        <textarea
          className={contextClass}
          value={formState.situationalFacts}
          onChange={
            isCustomMode
              ? (e) => {
                  updateForm({ situationalFacts: e.target.value });
                }
              : undefined
          }
          placeholder={t('situation.context.placeholder')}
          rows={16}
          readOnly={!isCustomMode}
          disabled={!isCustomMode}
        />
      </div>
    </div>
  );
}
