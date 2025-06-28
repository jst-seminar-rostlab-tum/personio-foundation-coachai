import { Suspense } from 'react';
import type { Metadata } from 'next';
import { generateMetadata as generateDynamicMetadata } from '@/lib/metadata';
import { MetadataProps } from '@/interfaces/MetadataProps';
import { adminService } from '@/services/server/AdminService';
import { reviewService } from '@/services/server/ReviewService';
import { api } from '@/services/server/Api';
import { UserProfileService } from '@/services/server/UserProfileService';
import { AccountRole } from '@/interfaces/UserProfile';
import { redirect } from 'next/navigation';
import StatCard from '@/components/common/StatCard';
import { getTranslations } from 'next-intl/server';
import AdminLoadingPage from './loading';
import TokenSetter from './components/TokenSetter';
import Reviews from './components/Reviews';
import UserManagement from './components/UserManagement';

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/admin', true);
}

export default async function AdminPage() {
  const userProfile = await UserProfileService.getUserProfile();
  if (userProfile.accountRole !== AccountRole.admin) {
    return redirect('/dashboard');
  }

  const PAGE_SIZE = 4;
  const statsData = adminService.getAdminStats();
  const reviewsData = reviewService.getPaginatedReviews(api, 1, PAGE_SIZE, 'newest');
  const [stats, reviews] = await Promise.all([statsData, reviewsData]);
  const t = await getTranslations('Admin');
  const statsArray = [
    { value: stats.totalUsers, label: t('statActiveUsers') },
    { value: stats.totalTrainings, label: t('statTotalTrainings') },
    { value: stats.totalReviews, label: t('statReviews') },
    { value: `${stats.averageScore}%`, label: t('statAverageScore') },
  ];

  return (
    <Suspense fallback={<AdminLoadingPage />}>
      <div className="max-w-full">
        <div className="text-2xl font-bold text-bw-70 text-center mb-2">{t('dashboardTitle')}</div>
        <div className="text-sm text-bw-40 text-center mb-8">{t('dashboardSubtitle')}</div>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {statsArray.map((stat, i) => (
            <StatCard key={i} value={stat.value} label={stat.label} />
          ))}
        </div>
        <TokenSetter dailyTokenLimit={stats.dailyTokenLimit} />
        <Reviews {...reviews} />
        <UserManagement />
      </div>
    </Suspense>
  );
}
