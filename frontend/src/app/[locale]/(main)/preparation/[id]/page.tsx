import { generateMetadata as generateDynamicMetadata } from '@/lib/utils/metadata';
import type { Metadata } from 'next';
import { api } from '@/services/ApiServer';
import { UserProfileService } from '@/services/UserProfileService';
import SessionLimitReached from '@/components/common/SessionLimitReached';
import { MetadataProps } from '@/interfaces/props/MetadataProps';
import { getTranslations } from 'next-intl/server';
import PreparationContent from './components/PreparationContent';

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/preparation', true);
}

export default async function PreparationPage() {
  const t = await getTranslations('Preparation');
  const tCommon = await getTranslations('Common');

  const userStats = await UserProfileService.getUserStats(api);

  if (userStats.numRemainingDailySessions === 0) {
    return <SessionLimitReached />;
  }

  return (
    <div className="flex flex-col gap-8">
      <h1 className="text-2xl text-center">{t('title')}</h1>

      <PreparationContent />

      <div className="mt-4 text-center">
        <p className="text-xs text-bw-40">{tCommon('aiDisclaimer')}</p>
      </div>
    </div>
  );
}
