import { Suspense } from 'react';
import type { Metadata } from 'next';
import { generateMetadata as generateDynamicMetadata } from '@/lib/metadata';
import { MetadataProps } from '@/interfaces/props/MetadataProps';
import { adminService } from '@/services/server/AdminService';
import { reviewService } from '@/services/server/ReviewService';
import { api } from '@/services/server/Api';
import { UserProfileService } from '@/services/server/UserProfileService';
import { AccountRole } from '@/interfaces/UserProfile';
import { redirect } from 'next/navigation';
import Admin from './components/AdminPage';
import AdminLoadingPage from './loading';

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

  return (
    <Suspense fallback={<AdminLoadingPage />}>
      <Admin stats={stats} reviews={reviews} />
    </Suspense>
  );
}
