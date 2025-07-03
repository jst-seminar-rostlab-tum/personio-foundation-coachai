import { generateMetadata as generateDynamicMetadata } from '@/lib/utils/metadata';
import type { Metadata } from 'next';
import { MetadataProps } from '@/interfaces/props/MetadataProps';
import { PagesProps } from '@/interfaces/props/PagesProps';
import SimulationPageComponent from './components/SimulationPage';

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/simulation/[id]', true);
}

export default async function SimulationPage(props: PagesProps) {
  const { id } = await props.params;

  return <SimulationPageComponent sessionId={id} />;
}
