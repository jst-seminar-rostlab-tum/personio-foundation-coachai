import { generateMetadata as generateDynamicMetadata } from '@/lib/metadata';
import type { Metadata } from 'next';
import { ArrowLeftIcon } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { MetadataProps } from '@/interfaces/props/MetadataProps';
import { PagesProps } from '@/interfaces/props/PagesProps';
import { getTranslations } from 'next-intl/server';
import PreparationContent from './components/PreparationContent';
import { CreateSessionButton } from './components/CreateSessionButton';

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/preparation', true);
}

export default async function PreparationPage(props: PagesProps) {
  const t = await getTranslations('Preparation');
  const tCommon = await getTranslations('Common');

  const { id } = await props.params;
  return (
    <div className="flex flex-col gap-8 p-8">
      <h1 className="text-2xl text-center">{t('title')}</h1>

      <PreparationContent />

      <div className="flex gap-4">
        <Link href="/new-conversation-scenario" className="flex-1">
          <Button size="full" variant="outline">
            <ArrowLeftIcon />
            {tCommon('back')}
          </Button>
        </Link>

        <CreateSessionButton scenarioId={id} />
      </div>
    </div>
  );
}
