import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { ArrowRight } from 'lucide-react';
import { useTranslations } from 'next-intl';

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
        <nav className="hidden md:flex items-center gap-6">
          <Button asChild variant="default">
            <Link href="/login">
              <span className="text-sm">{t('header.getStarted')}</span>
            </Link>
          </Button>
        </nav>
        <div className="md:hidden">
          <Link href="/login">
            <button className="inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-full text-sm font-medium transition-colors disabled:pointer-events-none disabled:opacity-50 h-8 w-8 bg-marigold-30">
              <ArrowRight className="h-5 w-5" />
            </button>
          </Link>
        </div>
      </div>
    </header>
  );
}
