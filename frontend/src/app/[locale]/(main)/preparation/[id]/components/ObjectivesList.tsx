import { Goal } from 'lucide-react';
import { useTranslations } from 'next-intl';

/**
 * Props for the objectives list.
 */
interface ObjectivesListProps {
  objectives: string[];
}

/**
 * Displays the scenario objectives as a bullet list.
 */
export default function ObjectivesList({ objectives }: ObjectivesListProps) {
  const tCommon = useTranslations('Common');

  return (
    <div className="space-y-4">
      {objectives.map((label, i) => (
        <div key={i} className="flex items-center gap-3">
          <Goal className="text-bw-70 size-4 shrink-0" />
          <span className="text-base text-bw-70">{label}</span>
        </div>
      ))}
      <div className="mt-3">
        <p className="text-xs text-bw-50">{tCommon('aiGeneratedDisclaimer')}</p>
      </div>
    </div>
  );
}
