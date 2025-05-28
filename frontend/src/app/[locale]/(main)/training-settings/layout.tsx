import type { Metadata } from 'next';
import { generateMetadata as generateDynamicMetadata } from '@/lib/metadata';

type Props = {
  params: Promise<{ locale: string }>;
};

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale } = await params;

  return generateDynamicMetadata(locale, '/training-settings', true);
}

export default function TrainingSettingsLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
