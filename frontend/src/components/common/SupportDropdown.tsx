'use client';

import { HelpCircle, Mail } from 'lucide-react';
import { useTranslations } from 'next-intl';
import { Select, SelectContent, SelectItem, SelectTrigger } from '../ui/Select';

interface SupportDropdownProps {
  onHelpClick: () => void;
  onContactClick: () => void;
}

export function SupportDropdown({ onHelpClick, onContactClick }: SupportDropdownProps) {
  const tCommon = useTranslations('Common');

  const handleValueChange = (value: string) => {
    if (value === 'help') {
      onHelpClick();
    } else if (value === 'contact') {
      onContactClick();
    }
  };

  return (
    <Select onValueChange={handleValueChange} value="">
      <SelectTrigger
        className="h-8 w-auto gap-2 px-3 py-1.5 text-xs font-medium !border-solid !border !border-bw-40 bg-custom-beige hover:bg-bw-10 focus:ring-1 focus:ring-forest-70 transition-colors"
        variant="minimal"
      >
        <HelpCircle className="w-4 h-4" />
        <span>{tCommon('support')}</span>
      </SelectTrigger>
      <SelectContent className="bg-white min-w-[180px]">
        <SelectItem value="help" className="text-sm data-[highlighted]:bg-custom-beige">
          <div className="flex items-center gap-2">
            <HelpCircle className="w-4 h-4" />
            <span>{tCommon('help')}</span>
          </div>
        </SelectItem>
        <SelectItem value="contact" className="text-sm data-[highlighted]:bg-custom-beige">
          <div className="flex items-center gap-2">
            <Mail className="w-4 h-4" />
            <span>{tCommon('contact')}</span>
          </div>
        </SelectItem>
      </SelectContent>
    </Select>
  );
}
