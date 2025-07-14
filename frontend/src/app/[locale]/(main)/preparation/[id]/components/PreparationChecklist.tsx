import Checkbox from '@/components/ui/Checkbox';
import { useTranslations } from 'next-intl';

interface PreparationChecklistProps {
  checklist: string[];
}

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
        <p className="text-xs text-bw-40">{tCommon('aiGeneratedDisclaimer')}</p>
      </div>
    </div>
  );
}
