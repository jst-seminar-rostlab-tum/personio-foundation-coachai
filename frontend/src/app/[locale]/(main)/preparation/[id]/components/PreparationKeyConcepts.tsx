import { KeyConcept } from '@/interfaces/models/ConversationScenario';
import { useTranslations } from 'next-intl';

/**
 * Props for the key concepts list.
 */
interface PreparationKeyConceptsProps {
  keyConcepts: KeyConcept[];
}

/**
 * Displays key concepts with headings and descriptions.
 */
export default function PreparationKeyConcepts({ keyConcepts }: PreparationKeyConceptsProps) {
  const tCommon = useTranslations('Common');

  return (
    <div className="space-y-4">
      {keyConcepts.map((concept, index) => (
        <div key={index} className="flex flex-col gap-2">
          <label
            htmlFor={`check-${index}`}
            className="text-lg font-bold text-bw-70 leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
          >
            {concept.header}
          </label>
          <p className="text-base text-bw-70">{concept.value}</p>
        </div>
      ))}
      <div className="mt-3">
        <p className="text-xs text-bw-50">{tCommon('aiGeneratedDisclaimer')}</p>
      </div>
    </div>
  );
}
