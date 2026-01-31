'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { ArrowRight } from 'lucide-react';
import { useTranslations } from 'next-intl';
import { usePathname } from 'next/navigation';
import Image from 'next/image';
import { LanguageSwitcher } from '../common/LanguageSwitcher';
import { HighlightedAppName } from '../common/HighlightedAppName';

/**
 * Renders the public about header with branding and locale switcher.
 */
export default function AboutHeader() {
  const t = useTranslations('HomePage');
  const pathname = usePathname();
  const isLoginPath = pathname.includes('/login');

  return (
    <header className="sticky top-0 z-50 w-full bg-marigold-5 mb-1 shadow">
      <div className="flex h-16 items-center justify-between mx-auto px-[clamp(1.25rem,4vw,4rem)] max-w-7xl">
        <div className="flex items-center gap-3">
          <Link href="/" className="text-bw-70 text-xl font-semibold">
            <HighlightedAppName />
          </Link>
          <div className="h-8 w-px bg-black"></div>
          <Image
            src="/images/logos/personio-foundation.svg"
            alt="Personio Foundation"
            width={100}
            height={100}
            className="flex-shrink-0"
          />
        </div>

        <div className="flex items-center gap-2 md:gap-4">
          <LanguageSwitcher />
          {!isLoginPath && (
            <div>
              <nav className="hidden md:flex items-center gap-6">
                <Button asChild>
                  <Link href="/login">
                    <span className="text-sm">{t('getStarted')}</span>
                  </Link>
                </Button>
              </nav>
              <div className="md:hidden">
                <Link href="/login">
                  <Button size="icon">
                    <ArrowRight className="h-5 w-5" strokeWidth={2.3} />
                  </Button>
                </Link>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
