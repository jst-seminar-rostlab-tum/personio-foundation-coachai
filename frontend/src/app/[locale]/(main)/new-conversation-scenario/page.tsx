import { generateMetadata as generateDynamicMetadata } from '@/lib/utils/metadata';
import type { Metadata } from 'next';
import { MetadataProps } from '@/interfaces/props/MetadataProps';
import { api } from '@/services/ApiServer';
import { UserProfileService } from '@/services/UserProfileService';
import SessionLimitReached from '@/components/common/SessionLimitReached';
import ConversationScenarioForm from './components/ConversationScenarioForm';

/**
 * Generates localized metadata for the new conversation scenario page.
 */
export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/new-conversation-scenario', true);
}

/**
 * Renders the new scenario form or a session limit warning.
 */
export default async function ConversationScenarioPage() {
  const userProfilePromise = UserProfileService.getUserProfile(api);
  const userStatsPromise = UserProfileService.getUserStats(api);
  const [userProfile, userStats] = await Promise.all([userProfilePromise, userStatsPromise]);
  const isAdmin = userProfile.accountRole === 'admin';
  if (userStats.numRemainingDailySessions === 0 && !isAdmin) {
    return <SessionLimitReached />;
  }

  return <ConversationScenarioForm />;
}
