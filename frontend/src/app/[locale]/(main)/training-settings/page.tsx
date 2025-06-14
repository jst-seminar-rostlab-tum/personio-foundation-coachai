import { generateMetadata as generateDynamicMetadata } from '@/lib/metadata';
import type { Metadata } from 'next';
import { MetadataProps } from '@/interfaces/MetadataProps';
import { UserProfileService } from '@/services/UserProfileService';
import { Suspense } from 'react';
import TrainingSettings from './components/TrainingSettings';
import TrainingSettingsLoadingPage from './loading';

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/training-settings', true);
}

export default function TrainingSettingsPage() {
  const userProfile = UserProfileService.getUserProfile();
  return (
    <Suspense fallback={<TrainingSettingsLoadingPage />}>
      <TrainingSettings userProfile={userProfile}></TrainingSettings>
    </Suspense>
  );
}
