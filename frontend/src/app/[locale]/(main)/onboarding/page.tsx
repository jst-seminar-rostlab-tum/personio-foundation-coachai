import { generateMetadata as generateDynamicMetadata } from '@/lib/metadata';
import type { Metadata } from 'next';
import type { Props } from '@/interfaces/Props';
import OnboardingPageComponent from '@/components/common/OnboardingPage';

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/onboarding', true);
}

export default function OnboardingPage() {
  return <OnboardingPageComponent />;
}
