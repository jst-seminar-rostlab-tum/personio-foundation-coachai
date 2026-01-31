import { generateMetadata as generateDynamicMetadata } from '@/lib/utils/metadata';
import type { Metadata } from 'next';
import { MetadataProps } from '@/interfaces/props/MetadataProps';
import { PagesProps } from '@/interfaces/props/PagesProps';
import { sessionService } from '@/services/SessionService';
import { api } from '@/services/ApiServer';
import SessionPageComponent from './components/SessionPage';

/**
 * Generates localized metadata for the live session page.
 */
export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/session/[id]', true);
}

/**
 * Loads session realtime data and renders the live session UI.
 */
export default async function SessionPage(props: PagesProps) {
  const { id } = await props.params;
  const sessionRealtime = await sessionService.getSessionRealtime(api, id);

  return (
    <SessionPageComponent
      sessionId={id}
      personaName={sessionRealtime.data.persona_name}
      categoryName={sessionRealtime.data.category_name}
      ephemeralKey={sessionRealtime.data.value}
    />
  );
}
