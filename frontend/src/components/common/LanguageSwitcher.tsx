'use client';

import { useRouter, usePathname } from 'next/navigation';
import routing from '@/i18n/routing';
import { useLocale } from 'next-intl';
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '../ui/Select';

export function LanguageSwitcher() {
  const router = useRouter();
  const pathname = usePathname();
  const locale = useLocale();

  const onLocaleChange = (value: string) => {
    const pathnameWithoutLocale = pathname.replace(`/${locale}`, '');
    const newPath = `/${value}${pathnameWithoutLocale}`;
    router.push(newPath);
  };

  return (
    <Select value={locale} onValueChange={onLocaleChange}>
      <SelectTrigger className="h-8 w-14" variant="minimal">
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        {routing.locales.map((cur) => (
          <SelectItem key={cur} value={cur}>
            <span className="text-xl">{cur === 'en' ? '🇬🇧' : '🇩🇪'}</span>
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
