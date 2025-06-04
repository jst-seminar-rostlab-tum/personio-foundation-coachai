import { generateMetadata as generateDynamicMetadata } from '@/lib/metadata';
import type { Metadata } from 'next';
import type { Props } from '@/interfaces/LayoutProps';
import Admin from '@/components/common/AdminPage';

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/admin', true);
}

export default function AdminPage() {
  return <Admin />;
}
