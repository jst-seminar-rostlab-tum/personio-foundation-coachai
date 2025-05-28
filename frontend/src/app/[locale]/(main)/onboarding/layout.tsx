import { Metadata } from 'next';
import { generateMetadata as generateDynamicMetadata } from '@/lib/metadata';

type Props = {
  params: Promise<{ locale: string }>;
};

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale } = await params;

  return generateDynamicMetadata(locale, '/onboarding', true);
}

export default function OnboardingLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
