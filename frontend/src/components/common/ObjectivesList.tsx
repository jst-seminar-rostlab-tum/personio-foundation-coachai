'use client';

import { Goal } from 'lucide-react';
import { UserOption } from '@/interfaces/UserInputFields';

interface ObjectivesListProps {
  items: UserOption[];
}

export default function ObjectivesList({ items }: ObjectivesListProps) {
  return (
    <div className="space-y-4">
      {items.map((item) => (
        <div key={item.id} className="flex items-center gap-3">
          <Goal className="text-bw-70 size-4 shrink-0" />
          <span className="text-base text-bw-70">{item.label}</span>
        </div>
      ))}
    </div>
  );
}
