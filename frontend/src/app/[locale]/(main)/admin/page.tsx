import { generateMetadata as generateDynamicMetadata } from '@/lib/metadata';
import type { Metadata } from 'next';
import { MetadataProps } from '@/interfaces/MetadataProps';
import BackButton from '@/components/common/BackButton';
import Admin from './components/AdminPage';

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/admin', true);
}

export default function AdminPage() {
  return (
    <>
      <BackButton />
      <Admin />
    </>
  );
}
