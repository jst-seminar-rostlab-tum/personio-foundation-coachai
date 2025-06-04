import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { ArrowRight } from 'lucide-react';
import { useTranslations } from 'next-intl';
import { LanguageSwitcher } from '../common/LanguageSwitcher';

export default function AboutHeader() {
  const t = useTranslations('HomePage');

  return (
    <header className="sticky top-0 z-50 w-full bg-white mb-1">
      <div className="container flex h-16 items-center justify-between mx-auto px-4">
        <div className="flex items-center gap-2">
          <Link href="/" className="flex items-center gap-2">
            <span className="text-xl font-semibold text-black">{t('header.appName')}</span>
          </Link>
        </div>
        <div className="flex items-center gap-2 md:gap-4">
          <LanguageSwitcher />
          <nav className="hidden md:flex items-center gap-6">
            <Button asChild>
              <Link href="/login">
                <span className="text-sm">{t('header.getStarted')}</span>
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
      </div>
    </header>
  );
}
