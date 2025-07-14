import { Textarea } from '@/components/ui/Textarea';

export const PersonaTextarea = ({
  label,
  value,
  onChange,
  isCustomContextMode,
}: {
  label: string;
  value: string;
  onChange: (val: string) => void;
  isCustomContextMode: boolean;
}) => {
  const lockedClasses = `border border-bw-40 placeholder:text-muted-foreground flex field-sizing-content w-full rounded-md bg-white px-3 py-2 text-base shadow-xs transition-[color,box-shadow] outline-none ${
    isCustomContextMode ? '' : 'text-bw-60 cursor-not-allowed'
  } resize-none overflow-auto`;

  return (
    <div className="w-full sm:flex-1 min-w-0">
      <label className="mb-2 font-medium text-lg block">{label}</label>
      <Textarea
        className={lockedClasses}
        value={value}
        onChange={(e) => isCustomContextMode && onChange(e.target.value)}
        disabled={!isCustomContextMode}
        rows={5}
        style={{ resize: 'none' }}
      />
    </div>
  );
};
