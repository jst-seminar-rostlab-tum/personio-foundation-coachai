import { generateMetadata as generateDynamicMetadata } from '@/lib/metadata';
import type { Metadata } from 'next';
import { MetadataProps } from '@/interfaces/MetadataProps';
import { api } from '@/services/ApiServer';
import { adminService } from '@/services/AdminService';
import Admin from './components/AdminPage';

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/admin', true);
}

export default function AdminPage() {
  const stats = adminService.getAdminStats(api);
  return <Admin stats={stats} />;
}
