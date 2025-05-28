import { Metadata } from 'next';
import { getTranslations } from 'next-intl/server';

const BASE_URL = process.env.NEXT_PUBLIC_BASE_URL || 'https://personiofoundation-coachai.com';

function getNamespaceFromPath(path: string): string {
  const cleanPath = path.replace(/^\/|\/$/g, '');
  const segments = cleanPath.split('/');

  if (segments.length === 0 || segments[0] === '') return 'HomePage';

  const isLocalizedPath = ['en', 'de'].includes(segments[0]);
  const pathSegment = isLocalizedPath ? segments[1] : segments[0];

  const pathMap: Record<string, string> = {
    '': 'HomePage',
    admin: 'Admin',
    dashboard: 'Dashboard',
    feedback: 'Feedback',
    history: 'History',
    login: 'Login',
    'new-training': 'NewTraining',
    onboarding: 'Onboarding',
    preparation: 'Preparation',
    simulation: 'Simulation',
    'training-settings': 'TrainingSettings',
  };

  return pathMap[pathSegment] || 'HomePage';
}

export async function generateMetadata(
  locale: string,
  path: string,
  isAuthenticated: boolean = false
): Promise<Metadata> {
  const url = `${BASE_URL}${path}`;
  const localizedUrl = locale === 'en' ? url : `${BASE_URL}/${locale}${path}`;

  const namespace = getNamespaceFromPath(path);
  const t = await getTranslations({ locale, namespace });

  const baseMetadata = {
    title: t('metaTitle') || 'Coach AI',
    description: t('metaDescription') || 'AI-powered coaching platform for leadership development',
    metadataBase: new URL(BASE_URL),
    alternates: {
      canonical: localizedUrl,
      languages: {
        'en-US': url,
        de: `${BASE_URL}/de${path}`,
        'x-default': url,
      },
    },
    manifest: '/manifest.json',
    icons: {
      icon: [
        {
          url: '/icons/personio_foundation_favicon.png',
          type: 'image/png',
        },
      ],
      shortcut: '/icons/personio_foundation_favicon.png',
      apple: '/icons/personio_foundation_favicon.png',
    },
  };

  if (isAuthenticated) {
    return {
      ...baseMetadata,
      robots: {
        index: false,
        follow: false,
        nocache: true,
        googleBot: {
          index: false,
          follow: false,
          noimageindex: true,
        },
      },
    };
  }

  return {
    ...baseMetadata,
    robots: {
      index: true,
      follow: true,
    },
  };
}
