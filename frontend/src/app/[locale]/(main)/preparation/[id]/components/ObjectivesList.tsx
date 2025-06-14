import { Goal } from 'lucide-react';

export default function ObjectivesList({ objectives }: { objectives: string[] }) {
  return (
    <div className="space-y-4">
      {objectives.map((label, i) => (
        <div key={i} className="flex items-center gap-3">
          <Goal className="text-bw-70 size-4 shrink-0" />
          <span className="text-base text-bw-70">{label}</span>
        </div>
      ))}
    </div>
  );
}
