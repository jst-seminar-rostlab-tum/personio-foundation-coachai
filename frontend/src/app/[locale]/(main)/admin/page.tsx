import { Suspense } from 'react';
import type { Metadata } from 'next';
import { generateMetadata as generateDynamicMetadata } from '@/lib/utils/metadata';
import { MetadataProps } from '@/interfaces/props/MetadataProps';
import { adminService } from '@/services/AdminService';
import { reviewService } from '@/services/ReviewService';
import { UserProfileService } from '@/services/UserProfileService';
import { AccountRole } from '@/interfaces/models/UserProfile';
import { redirect } from 'next/navigation';
import StatCard from '@/components/common/StatCard';
import { getTranslations } from 'next-intl/server';
import { api } from '@/services/ApiServer';
import AdminLoadingPage from './loading';
import TokenSetter from './components/TokenSetter';
import Reviews from './components/Reviews';
import UserManagement from './components/UserManagement';

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/admin', true);
}

export default async function AdminPage() {
  const userProfile = await UserProfileService.getUserProfile(api);
  if (userProfile.accountRole !== AccountRole.admin) {
    return redirect('/dashboard');
  }

  const PAGE_SIZE = 4;
  const statsData = adminService.getAdminStats(api);
  const reviewsData = reviewService.getPaginatedReviews(api, 1, PAGE_SIZE, 'newest');
  const usersData = UserProfileService.getPaginatedUsers(api, 1, PAGE_SIZE);
  const [stats, reviews, users] = await Promise.all([statsData, reviewsData, usersData]);
  const t = await getTranslations('Admin');
  const tCommon = await getTranslations('Common');
  const statsArray = [
    { value: stats.totalUsers, label: t('statActiveUsers') },
    { value: stats.totalTrainings, label: tCommon('totalSessions') },
    { value: stats.totalReviews, label: tCommon('reviews') },
    { value: `${stats.averageScore}%`, label: tCommon('avgScore') },
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
        <UserManagement usersPaginationData={users} />
      </div>
    </Suspense>
  );
}
