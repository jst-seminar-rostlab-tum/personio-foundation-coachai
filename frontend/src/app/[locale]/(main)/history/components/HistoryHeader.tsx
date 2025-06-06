import { useTranslations } from 'next-intl';

export default function HistoryHeader() {
  const t = useTranslations('History');

  return (
    <div className="flex flex-col items-center md:items-start gap-1 px-4 pt-6 pb-4 text-center md:text-left">
      <div className="text-2xl font-bold text-bw-70">{t('title')}</div>
      <div className="text-sm text-bw-40">{t('subtitle')}</div>
    </div>
  );
}
