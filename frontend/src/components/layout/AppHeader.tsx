'use client';

import { Menu, X } from 'lucide-react';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useTranslations } from 'next-intl';
import { Button } from '../ui/Button';
import { LanguageSwitcher } from '../common/LanguageSwitcher';

export function AppHeader() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const t = useTranslations('AppHeader');

  const navigationLinks = [
    { key: 'dashboard', href: '/dashboard' },
    { key: 'newTraining', href: '/new-training' },
    { key: 'admin', href: '/admin' },
    { key: 'history', href: '/history' },
    { key: 'trainingSettings', href: '/training-settings' },
  ];

  useEffect(() => {
    if (isMenuOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isMenuOpen]);

  return (
    <>
      <header className="fixed top-0 left-0 right-0 bg-background z-50 shadow">
        <div className="md:max-w-5xl md:mx-auto flex items-center justify-between px-4 py-2 xl:px-0 min-h-[56px]">
          <Link
            href="/dashboard"
            className="text-bw-70 text-xl font-semibold"
            onClick={() => setIsMenuOpen(false)}
          >
            {t('title')}
          </Link>
          <div className="flex items-center gap-2">
            <LanguageSwitcher />
            <Button variant="ghost" size="icon" onClick={() => setIsMenuOpen(!isMenuOpen)}>
              {isMenuOpen ? <X className="!w-4 !h-4" /> : <Menu className="!w-4 !h-4" />}
            </Button>
          </div>
        </div>
      </header>

      <div
        className={`fixed inset-0 z-40 top-0 transition-transform duration-300 ease-in-out ${
          isMenuOpen ? 'translate-y-0' : '-translate-y-full'
        }`}
      >
        <div className="flex items-center justify-between px-4 py-2 xl:px-16 bg-background min-h-[56px]">
          <div className="text-bw-70 text-lg font-semibold">{t('title')}</div>
          <Button variant="ghost" size="icon" onClick={() => setIsMenuOpen(false)}>
            <X className="!w-4 !h-4" />
          </Button>
        </div>
        <div className="flex flex-col items-center justify-center h-[calc(100vh-56px)] bg-background-light">
          <nav className="flex flex-col items-center justify-center space-y-10">
            {navigationLinks.map(({ key, href }) => (
              <Link
                key={key}
                href={href}
                className="barlow-condensed-medium font-bold uppercase text-4xl md:text-5xl text-bw-70 hover:text-bw-50"
                onClick={() => setIsMenuOpen(false)}
              >
                {t(key)}
              </Link>
            ))}
          </nav>
        </div>
      </div>
    </>
  );
}
