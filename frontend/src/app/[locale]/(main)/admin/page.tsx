import { Suspense } from 'react';
import type { Metadata } from 'next';
import { generateMetadata as generateDynamicMetadata } from '@/lib/utils/metadata';
import { MetadataProps } from '@/interfaces/props/MetadataProps';
import { adminService } from '@/services/AdminService';
import { reviewService } from '@/services/ReviewService';
import { UserProfileService } from '@/services/UserProfileService';
import { getTranslations } from 'next-intl/server';
import { api } from '@/services/ApiServer';
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
  const PAGE_SIZE = 4;
  const statsData = adminService.getAdminStats(api);
  const reviewsData = reviewService.getPaginatedReviews(api, 1, PAGE_SIZE, 'newest');
  const usersData = UserProfileService.getPaginatedUsers(api, 1, PAGE_SIZE);
  const [stats, reviews, users] = await Promise.all([statsData, reviewsData, usersData]);
  const t = await getTranslations('Admin');

  return (
    <Suspense fallback={<AdminLoadingPage />}>
      <div className="max-w-full">
        <div className="text-2xl font-bold text-bw-70 text-center mb-2">{t('dashboardTitle')}</div>
        <div className="text-sm text-bw-40 text-center mb-8">{t('dashboardSubtitle')}</div>
        <AdminStatCards />
        <SessionSetter dailySessionLimit={stats.dailySessionLimit} />
        <Reviews {...reviews} />
        <UsersList {...users} />
      </div>
    </Suspense>
  );
}
