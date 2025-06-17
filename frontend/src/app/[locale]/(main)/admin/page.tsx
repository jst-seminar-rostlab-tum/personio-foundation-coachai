import { generateMetadata as generateDynamicMetadata } from '@/lib/metadata';
import type { Metadata } from 'next';
import { MetadataProps } from '@/interfaces/MetadataProps';
import { adminService } from '@/services/server/AdminService';
import { UserProfileService } from '@/services/server/UserProfileService';
import { AccountRole } from '@/interfaces/UserProfile';
import { redirect } from 'next/navigation';
import Admin from './components/AdminPage';

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/admin', true);
}

export default async function AdminPage() {
  const userProfile = await UserProfileService.getUserProfile();
  if (userProfile.accountRole !== AccountRole.admin) {
    return redirect('/dashboard');
  }

  const stats = adminService.getAdminStats();
  return <Admin stats={stats} />;
}
