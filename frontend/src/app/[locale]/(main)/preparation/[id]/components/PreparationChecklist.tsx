import Checkbox from '@/components/ui/Checkbox';
import { useTranslations } from 'next-intl';

/**
 * Props for the preparation checklist.
 */
interface PreparationChecklistProps {
  checklist: string[];
}

/**
 * Displays a checklist of preparation tasks.
 */
export default function PreparationChecklist({ checklist }: PreparationChecklistProps) {
  const tCommon = useTranslations('Common');

  return (
    <div className="space-y-4">
      {checklist.map((label, index) => (
        <div key={index} className="flex items-center gap-3">
          <Checkbox id={`check-${index}`} />
          <label
            htmlFor={`check-${index}`}
            className="text-base text-bw-70 leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
          >
            {label}
          </label>
        </div>
      ))}
      <div className="mt-3">
        <p className="text-xs text-bw-50">{tCommon('aiGeneratedDisclaimer')}</p>
      </div>
    </div>
  );
}
