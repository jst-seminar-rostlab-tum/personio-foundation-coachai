'use client';

import { Menu, X } from 'lucide-react';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { useUser } from '@/contexts/User';
import { AccountRole } from '@/interfaces/models/UserProfile';
import { createClient } from '@/lib/supabase/client';
import { logoutUser } from '@/lib/supabase/logout';
import { Button } from '../ui/Button';
import { LanguageSwitcher } from '../common/LanguageSwitcher';

export function AppHeader() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const tCommon = useTranslations('Common');
  const pathname = usePathname();
  const user = useUser();
  const isAdmin = user?.accountRole === AccountRole.admin;

  const navigationLinks = [
    { key: 'dashboard', href: '/dashboard' },
    { key: 'newConversationScenario', href: '/new-conversation-scenario' },
    ...(isAdmin ? [{ key: 'admin', href: '/admin' }] : []),
    { key: 'settings', href: '/settings' },
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
      <header className="fixed top-0 left-0 right-0 bg-background z-50 shadow">
        <div className="flex h-16 items-center justify-between mx-auto px-[clamp(1.25rem,4vw,4rem)] max-w-7xl">
          <Link
            href="/dashboard"
            className="text-bw-70 text-xl font-semibold"
            onClick={() => setIsMenuOpen(false)}
          >
            {tCommon('appName')}
          </Link>
          <div className="flex items-center gap-6">
            {/* Navigation Elements */}
            <div className="hidden lg:flex items-center gap-10">
              {navigationLinks.map(({ key, href }) => (
                <Link
                  key={key}
                  href={href}
                  className="relative group text-bw-60 font-medium text-lg transition-colors cursor-pointer"
                >
                  {tCommon(key)}
                  <span
                    className={`block h-0.5 absolute left-1/2 -translate-x-1/2 -bottom-1 transition-transform duration-300 ease-in-out origin-left w-[90%] ${
                      pathname.includes(href)
                        ? 'scale-x-100 bg-marigold-50'
                        : 'scale-x-0 group-hover:scale-x-100 bg-bw-60'
                    }`}
                  />
                </Link>
              ))}
            </div>
            <LanguageSwitcher />
            {/* Burger Menu Item */}
            <Button
              className="lg:hidden p-0"
              variant="ghost"
              size="icon"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
            >
              {isMenuOpen ? <X className="!w-4 !h-4" /> : <Menu className="!w-4 !h-4" />}
            </Button>
            <Button
              variant="secondary"
              className="hidden lg:flex h-8"
              onClick={async () => {
                await logoutUser(createClient);
              }}
            >
              <span className="text-xs font-medium">{tCommon('logout')}</span>
            </Button>
          </div>
        </div>
      </header>

      {/* Mobile Navigator */}
      <div
        className={`lg:hidden fixed inset-0 z-40 top-0 transition-transform duration-300 ease-in-out ${
          isMenuOpen ? 'translate-y-0' : '-translate-y-full'
        }`}
      >
        <div className="flex items-center justify-between px-2 py-2 xl:px-16 bg-background min-h-[56px]">
          <div className="text-bw-70 text-lg font-semibold">{tCommon('appName')}</div>
          <Button variant="ghost" size="icon" onClick={() => setIsMenuOpen(false)}>
            <X className="!w-4 !h-4" />
          </Button>
        </div>
        <div className="flex flex-col items-center justify-center h-[calc(100vh-56px)] bg-background-light">
          <nav className="flex flex-col items-center justify-center space-y-10 sm:space-y-14">
            {navigationLinks.map(({ key, href }) => (
              <Link
                key={key}
                href={href}
                className={`bebas-neue font-bold uppercase text-4xl sm:text-5xl text-bw-70 transition-colors relative group`}
                onClick={() => setIsMenuOpen(false)}
              >
                {tCommon(key)}
                <span
                  className={`block h-1 sm:h-1.5 absolute left-1/2 -translate-x-1/2 -bottom-1 sm:-bottom-1.5 transition-transform duration-300 ease-in-out origin-left w-[95%] ${
                    pathname.includes(href)
                      ? 'scale-x-100 bg-marigold-50'
                      : 'scale-x-0 group-hover:scale-x-100 bg-bw-60'
                  }`}
                />
              </Link>
            ))}
            <span
              className="bebas-neue font-bold uppercase text-4xl sm:text-5xl text-bw-70 transition-colors relative group cursor-pointer"
              onClick={async () => {
                await logoutUser(createClient);
                setIsMenuOpen(false);
              }}
            >
              {tCommon('logout')}
              <span className="block h-1 sm:h-1.5 bg-bw-60 absolute left-1/2 -translate-x-1/2 -bottom-1 sm:-bottom-1.5 transition-transform duration-300 ease-in-out origin-left scale-x-0 group-hover:scale-x-100 w-[95%]" />
            </span>
          </nav>
        </div>
      </div>
    </>
  );
}
