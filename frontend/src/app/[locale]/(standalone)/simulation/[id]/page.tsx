import { generateMetadata as generateDynamicMetadata } from '@/lib/utils/metadata';
import type { Metadata } from 'next';
import { MetadataProps } from '@/interfaces/props/MetadataProps';
import { PagesProps } from '@/interfaces/props/PagesProps';
import { getTranslations } from 'next-intl/server';
import { sessionService } from '@/services/SessionService';
import { api } from '@/services/ApiServer';
import SimulationPageComponent from './components/SimulationPage';

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/simulation/[id]', true);
}

export default async function SimulationPage(props: PagesProps) {
  const { id } = await props.params;
  const tCommon = await getTranslations('Common');
  const sessionRealtime = await sessionService.getSessionRealtime(api, id);

  return (
    <div>
      <SimulationPageComponent
        personaName={sessionRealtime.data.persona_name}
        categoryName={sessionRealtime.data.category_name}
        sessionId={id}
      />
      <div className="mt-4 mb-4 text-center">
        <p className="text-xs text-bw-40">{tCommon('aiDisclaimer')}</p>
      </div>
    </div>
  );
}
