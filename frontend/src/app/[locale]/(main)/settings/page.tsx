import { generateMetadata as generateDynamicMetadata } from '@/lib/utils/metadata';
import type { Metadata } from 'next';
import { MetadataProps } from '@/interfaces/props/MetadataProps';
import { UserProfileService } from '@/services/UserProfileService';
import { Suspense } from 'react';
import { api } from '@/services/ApiServer';
import Settings from './components/Settings';
import SettingsLoadingPage from './loading';

/**
 * Generates localized metadata for the settings page.
 */
export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/settings', true);
}

/**
 * Renders the settings page with a suspense boundary.
 */
export default function SettingsPage() {
  const userProfile = UserProfileService.getUserProfile(api);
  return (
    <Suspense fallback={<SettingsLoadingPage />}>
      <Settings userProfile={userProfile}></Settings>
    </Suspense>
  );
}
