'use client';

import { Menu, X } from 'lucide-react';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useTranslations } from 'next-intl';
import { authService } from '@/services/client/AuthService';
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
    const lockBodyScroll = () => {
      const isMobile = window.matchMedia('(max-width: 767px)').matches;
      if (isMenuOpen && isMobile) {
        document.body.style.overflow = 'hidden';
      } else {
        document.body.style.overflow = '';
      }
    };
    lockBodyScroll();
    window.addEventListener('resize', lockBodyScroll);
    return () => {
      document.body.style.overflow = '';
      window.removeEventListener('resize', lockBodyScroll);
    };
  }, [isMenuOpen]);

  return (
    <>
      <header className="sticky top-0 left-0 right-0 bg-background z-50 shadow">
        <div className="md:max-w-5xl md:mx-auto flex items-center justify-between px-4 py-2 xl:px-0 min-h-[56px]">
          <Link
            href="/dashboard"
            className="text-bw-70 text-xl font-semibold"
            onClick={() => setIsMenuOpen(false)}
          >
            {t('title')}
          </Link>
          <div className="flex items-center gap-0 md:gap-4">
            <div className="hidden md:flex items-center gap-6">
              {navigationLinks.map(({ key, href }) => (
                <Link
                  key={key}
                  href={href}
                  className="text-bw-60 hover:text-marigold-50 font-medium text-lg"
                >
                  {t(key)}
                </Link>
              ))}
            </div>
            <LanguageSwitcher />
            <Button
              className="md:hidden pl-0"
              variant="ghost"
              size="icon"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
            >
              {isMenuOpen ? <X className="!w-4 !h-4" /> : <Menu className="!w-4 !h-4" />}
            </Button>
            <Button
              variant="secondary"
              className="hidden md:flex h-8"
              onClick={async () => {
                await authService.logoutUser();
              }}
            >
              <span className="text-xs font-medium">{t('logout')}</span>
            </Button>
          </div>
        </div>
      </header>

      <div
        className={`md:hidden fixed inset-0 z-40 top-0 transition-transform duration-300 ease-in-out ${
          isMenuOpen ? 'translate-y-0' : '-translate-y-full'
        }`}
      >
        <div className="flex items-center justify-between px-2 py-2 xl:px-16 bg-background min-h-[56px]">
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
                className="bebas-neue font-bold uppercase text-4xl md:text-5xl text-bw-70 hover:text-bw-50"
                onClick={() => setIsMenuOpen(false)}
              >
                {t(key)}
              </Link>
            ))}
            <span
              className="bebas-neue font-bold uppercase text-4xl md:text-5xl text-bw-70 hover:text-bw-50"
              onClick={async () => {
                await authService.logoutUser();
                setIsMenuOpen(false);
              }}
            >
              {t('logout')}
            </span>
          </nav>
        </div>
      </div>
    </>
  );
}
