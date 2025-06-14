import { generateMetadata as generateDynamicMetadata } from '@/lib/metadata';
import type { Metadata } from 'next';
import { MetadataProps } from '@/interfaces/MetadataProps';
import BackButton from '@/components/common/BackButton';
import OnboardingPageComponent from './components/OnboardingPage';

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/onboarding', true);
}

export default function OnboardingPage() {
  return (
    <>
      <BackButton />
      <OnboardingPageComponent />
    </>
  );
}
