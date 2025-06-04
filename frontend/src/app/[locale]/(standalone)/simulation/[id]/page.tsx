import SimulationPageComponent from '@/components/common/SimulationPage';
import { generateMetadata as generateDynamicMetadata } from '@/lib/metadata';
import type { Metadata } from 'next';
import { MetadataProps } from '@/interfaces/MetadataProps';

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/simulation/[id]', true);
}

export default function SimulationPage() {
  return <SimulationPageComponent />;
}
