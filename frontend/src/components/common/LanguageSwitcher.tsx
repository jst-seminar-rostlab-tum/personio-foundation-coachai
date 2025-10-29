'use client';

import { usePathname } from '@/i18n/navigation';
import routing from '@/i18n/routing';
import { useLocale } from 'next-intl';
import Image from 'next/image';
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '../ui/Select';

export function LanguageSwitcher() {
  const pathname = usePathname();
  const locale = useLocale();

  const onLocaleChange = (value: string) => {
    const newPath = `/${value}${pathname}`;
    window.location.href = newPath;
  };

  return (
    <Select value={locale} onValueChange={onLocaleChange}>
      <SelectTrigger className="h-8 w-16 hover:bg-bw-10" variant="minimal">
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        {routing.locales.map((cur) => (
          <SelectItem key={cur} value={cur} className="data-[highlighted]:bg-custom-beige">
            <Image
              src={
                cur === 'en' ? '/images/common/english-flag.svg' : '/images/common/german-flag.svg'
              }
              alt={cur === 'en' ? 'English' : 'German'}
              width={20}
              height={20}
              priority
            />
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
