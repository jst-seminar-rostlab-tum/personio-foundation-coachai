'use client';

import { useState } from 'react';
import Checkbox from '@/components/ui/Checkbox';
import { UserOption } from '@/interfaces/UserInputFields';

interface PreparationChecklistProps {
  items: UserOption[];
}

export default function PreparationChecklist({ items }: PreparationChecklistProps) {
  const [checkedItems, setCheckedItems] = useState<{ [key: string]: boolean }>(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('preparationChecklist');
      return saved ? JSON.parse(saved) : {};
    }
    return {};
  });

  const handleCheckChange = (id: string, checked: boolean) => {
    const newCheckedItems = { ...checkedItems, [id]: checked };
    setCheckedItems(newCheckedItems);
    if (typeof window !== 'undefined') {
      localStorage.setItem('preparationChecklist', JSON.stringify(newCheckedItems));
    }
  };

  return (
    <div className="space-y-4">
      {items.map((item) => (
        <div key={item.id} className="flex items-center gap-3">
          <Checkbox
            id={item.id}
            checked={checkedItems[item.id] || false}
            onCheckedChange={(checked) => handleCheckChange(item.id, checked as boolean)}
          />
          <label
            htmlFor={item.id}
            className="text-base text-bw-70 leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
          >
            {item.label}
          </label>
        </div>
      ))}
    </div>
  );
}
