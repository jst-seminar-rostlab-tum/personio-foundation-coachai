import { Suspense } from 'react';
import type { Metadata } from 'next';
import { generateMetadata as generateDynamicMetadata } from '@/lib/utils/metadata';
import { MetadataProps } from '@/interfaces/props/MetadataProps';
import { adminService } from '@/services/AdminService';
import { reviewService } from '@/services/ReviewService';
import { UserProfileService } from '@/services/UserProfileService';
import { getTranslations } from 'next-intl/server';
import { api } from '@/services/ApiServer';
import { REVIEWS_LIMIT, USER_LIST_LIMIT } from './constants/UsersList';
import AdminLoadingPage from './loading';
import SessionSetter from './components/SessionSetter';
import Reviews from './components/Reviews';
import UsersList from './components/UsersList';
import AdminStatCards from './components/AdminStatCards';

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/admin', true);
}

export default async function AdminPage() {
  const statsData = adminService.getAdminStats(api);
  const reviewsData = reviewService.getPaginatedReviews(api, 1, REVIEWS_LIMIT, 'newest');
  const usersData = UserProfileService.getPaginatedUsers(api, 1, USER_LIST_LIMIT);
  const [stats, reviews, users] = await Promise.all([statsData, reviewsData, usersData]);
  const t = await getTranslations('Admin');
  const tCommon = await getTranslations('Common');

  return (
    <Suspense fallback={<AdminLoadingPage />}>
      <div className="max-w-full">
        <div className="text-2xl font-bold text-bw-70 text-center mb-2">{t('dashboardTitle')}</div>
        <div className="text-sm text-bw-70 text-center mb-8">{t('dashboardSubtitle')}</div>
        <AdminStatCards />
        <div className="text-xl mt-16 font-medium text-bw-70">{tCommon('reviews')}</div>
        <Reviews {...reviews} />
        <div className="text-xl mb-6 mt-12 font-medium text-bw-70">{t('users')}</div>
        <SessionSetter defaultDailySessionLimit={stats.defaultDailySessionLimit} />
        <UsersList {...users} />
      </div>
    </Suspense>
  );
}
