import { generateMetadata as generateDynamicMetadata } from '@/lib/metadata';
import type { Metadata } from 'next';
import { MetadataProps } from '@/interfaces/props/MetadataProps';
import { UserProfileService } from '@/services/UserProfileService';
import { Suspense } from 'react';
import { api } from '@/services/ApiServer';
import Settings from './components/Settings';
import SettingsLoadingPage from './loading';

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/settings', true);
}

export default function SettingsPage() {
  const userProfile = UserProfileService.getUserProfile(api);
  return (
    <Suspense fallback={<SettingsLoadingPage />}>
      <Settings userProfile={userProfile}></Settings>
    </Suspense>
  );
}
