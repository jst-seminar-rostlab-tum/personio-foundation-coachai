import { Metadata } from 'next';
import { getTranslations } from 'next-intl/server';
import { BASE_URL } from '../connector';

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
    'new-conversation-scenario': 'ConversationScenario',
    onboarding: 'Onboarding',
    preparation: 'Preparation',
    privacy: 'PrivacyPolicy',
    simulation: 'Simulation',
    settings: 'Settings',
    terms: 'TermsOfService',
    confirm: 'Login.ConfirmationForm',
    reset: 'Reset',
    'update-password': 'UpdatePassword',
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
    keywords: [
      'Center for Software Engineering Excellence',
      'Personio Foundation',
      'CSEE',
      'leadership',
      'coaching',
      'AI',
      'training',
      'development',
      'feedback',
      'management',
    ],
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
          url: '/images/icons/personio-foundation-favicon.png',
          type: 'image/png',
        },
      ],
      shortcut: '/images/icons/personio-foundation-favicon.png',
      apple: '/images/icons/personio-foundation-favicon.png',
    },
    openGraph: {
      type: 'website',
      title: t('metaTitle') || 'Coach AI',
      description:
        t('metaDescription') || 'AI-powered coaching platform for leadership development',
      url: localizedUrl,
      siteName: 'Coach AI',
    },
    twitter: {
      card: 'summary',
      title: t('metaTitle') || 'Coach AI',
      description:
        t('metaDescription') || 'AI-powered coaching platform for leadership development',
      site: '@personio',
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
