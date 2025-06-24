import { generateMetadata as generateDynamicMetadata } from '@/lib/metadata';
import type { Metadata } from 'next';
import { MetadataProps } from '@/interfaces/MetadataProps';
import { UserProfileService } from '@/services/server/UserProfileService';
import { Suspense } from 'react';
import Settings from './components/Settings';
import SettingsLoadingPage from './loading';

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/settings', true);
}

export default function SettingsPage() {
  const userProfile = UserProfileService.getUserProfile();
  return (
    <Suspense fallback={<SettingsLoadingPage />}>
      <Settings userProfile={userProfile}></Settings>
    </Suspense>
  );
}
