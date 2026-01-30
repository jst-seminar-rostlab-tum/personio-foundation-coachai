import { generateMetadata as generateDynamicMetadata } from '@/lib/utils/metadata';
import type { Metadata } from 'next';
import { MetadataProps } from '@/interfaces/props/MetadataProps';
import OnboardingPageComponent from './components/OnboardingPage';

/**
 * Generates localized metadata for the onboarding page.
 */
export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/onboarding', true);
}

/**
 * Renders the onboarding flow container.
 */
export default function OnboardingPage() {
  return <OnboardingPageComponent />;
}
