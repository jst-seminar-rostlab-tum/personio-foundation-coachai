import { generateMetadata as generateDynamicMetadata } from '@/lib/utils/metadata';
import type { Metadata } from 'next';
import { MetadataProps } from '@/interfaces/props/MetadataProps';
import { PagesProps } from '@/interfaces/props/PagesProps';
import { getTranslations } from 'next-intl/server';
import { sessionService } from '@/services/SessionService';
import { api } from '@/services/ApiServer';
import SessionPageComponent from './components/SessionPage';

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/session/[id]', true);
}

export default async function SessionPage(props: PagesProps) {
  const { id } = await props.params;
  const tCommon = await getTranslations('Common');
  const sessionRealtime = await sessionService.getSessionRealtime(api, id);

  return (
    <div>
      <SessionPageComponent
        sessionId={id}
        personaName={sessionRealtime.data.persona_name}
        categoryName={sessionRealtime.data.category_name}
      />
      <div className="mt-4 mb-4 text-center">
        <p className="text-xs text-bw-40">{tCommon('aiDisclaimer')}</p>
      </div>
    </div>
  );
}
