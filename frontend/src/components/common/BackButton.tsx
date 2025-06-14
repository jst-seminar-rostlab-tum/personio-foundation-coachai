'use client';

import { ArrowLeftIcon } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { useRouter, usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { useEffect, useState } from 'react';

interface BackButtonProps {
  label?: string;
  href?: string;
  defaultLabel?: string;
}

const pageLabels: Record<string, Record<string, string>> = {
  en: {
    '/admin': 'Admin',
    '/dashboard': 'Dashboard',
    '/feedback': 'Feedback',
    '/history': 'History',
    '/new-training': 'New Training',
    '/onboarding': 'Onboarding',
    '/preparation': 'Preparation',
    '/training-settings': 'Training Settings',
  },
  de: {
    '/admin': 'Admin',
    '/dashboard': 'Dashboard',
    '/feedback': 'Feedback',
    '/history': 'Verlauf',
    '/new-training': 'Neues Training',
    '/onboarding': 'Onboarding',
    '/preparation': 'Vorbereitung',
    '/training-settings': 'Trainingseinstellungen',
  },
};

const getNavigationStack = (): string[] => {
  const stack = sessionStorage.getItem('navigationStack');
  return stack ? JSON.parse(stack) : [];
};

const getSuffix = (path: string): string => {
  const parts = path.split('/').filter(Boolean);

  if (parts[0]?.length === 2) {
    parts.shift();
  }
  return parts[parts.length - 1] || '';
};

const updateNavigationStack = (newPath: string) => {
  const stack = getNavigationStack();
  const suffix = getSuffix(newPath);

  if (suffix === 'dashboard' || suffix === 'admin') {
    const newStack = [suffix];
    sessionStorage.setItem('navigationStack', JSON.stringify(newStack));
    return newStack;
  }

  if (stack[stack.length - 1] !== suffix) {
    stack.push(suffix);

    const trimmedStack = stack.slice(-10);
    sessionStorage.setItem('navigationStack', JSON.stringify(trimmedStack));
  }

  return stack;
};

export default function BackButton({ label, href, defaultLabel = 'Back' }: BackButtonProps) {
  const router = useRouter();
  const pathname = usePathname();
  const [previousPath, setPreviousPath] = useState<string>('');
  const [isDisabled, setIsDisabled] = useState(true);

  useEffect(() => {
    if (!pathname) return;

    const currentStack = updateNavigationStack(pathname);

    if (currentStack.length > 1) {
      setPreviousPath(currentStack[currentStack.length - 2]);
      setIsDisabled(false);
    } else {
      setPreviousPath('');
      setIsDisabled(true);
    }
  }, [pathname]);

  useEffect(() => {
    const handlePopState = () => {
      const currentStack = getNavigationStack();
      if (currentStack.length > 0) {
        currentStack.pop();
        sessionStorage.setItem('navigationStack', JSON.stringify(currentStack));

        if (currentStack.length > 1) {
          setPreviousPath(currentStack[currentStack.length - 2]);
          setIsDisabled(false);
        } else {
          setPreviousPath('');
          setIsDisabled(true);
        }
      }
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const handleClick = () => {
    if (href) {
      router.push(href);
    } else if (previousPath && !isDisabled) {
      const parts = pathname.split('/').filter(Boolean);
      const hasLanguagePrefix = parts[0]?.length === 2;
      const currentLang = hasLanguagePrefix ? parts[0] : 'en';

      const localizedPath = hasLanguagePrefix
        ? `/${currentLang}/${previousPath}`
        : `/${previousPath}`;

      const currentStack = getNavigationStack();
      currentStack.pop();
      sessionStorage.setItem('navigationStack', JSON.stringify(currentStack));
      router.push(localizedPath);
    }
  };

  const getBackLabel = () => {
    if (label) return label;
    if (previousPath) {
      const parts = pathname.split('/').filter(Boolean);
      const hasLanguagePrefix = parts[0]?.length === 2;
      const currentLang = hasLanguagePrefix ? parts[0] : 'en';

      return (
        pageLabels[currentLang]?.[`/${previousPath}`] ||
        pageLabels.en[`/${previousPath}`] ||
        defaultLabel
      );
    }
    return defaultLabel;
  };

  if (isDisabled && !href) {
    return <div className="h-10" />;
  }

  return (
    <Button
      variant="ghost"
      className={cn(
        'group relative flex items-center gap-2 bg-transparent p-0 text-xl text-bw-40 transition-colors duration-200 hover:text-bw-70',
        'hover:bg-transparent',
        isDisabled && 'opacity-0 pointer-events-none'
      )}
      onClick={handleClick}
      disabled={isDisabled}
    >
      <ArrowLeftIcon className="h-4 w-4" strokeWidth={3} />
      <span className="relative transition-transform duration-200 group-hover:-translate-x-1">
        {getBackLabel()}
      </span>
    </Button>
  );
}
