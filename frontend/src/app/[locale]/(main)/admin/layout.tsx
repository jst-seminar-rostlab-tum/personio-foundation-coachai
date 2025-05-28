import type { Metadata } from 'next';
import { generateMetadata as generateDynamicMetadata } from '@/lib/metadata';

type Props = {
  params: Promise<{ locale: string }>;
};

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale } = await params;

  return generateDynamicMetadata(locale, '/admin', true);
}

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
