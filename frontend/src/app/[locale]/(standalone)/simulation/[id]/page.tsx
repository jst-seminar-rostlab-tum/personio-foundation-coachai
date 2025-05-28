import SimulationPageComponent from '@/components/common/SimulationPage';
import { generateMetadata as generateDynamicMetadata } from '@/lib/metadata';
import type { Metadata } from 'next';
import type { Props } from '@/interfaces/Props';

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/simulation/[id]', true);
}

export default function SimulationPage() {
  return <SimulationPageComponent />;
}
