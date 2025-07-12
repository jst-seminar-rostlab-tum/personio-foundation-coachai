'use client';

import { useTranslations } from 'next-intl';

export function StatisticsLabel() {
  const t = useTranslations('History');
  return <div className="text-xl font-bold text-bw-70">{t('statistics')}</div>;
}

export function PreviousSessionsLabel() {
  const t = useTranslations('History');
  return <div className="text-xl font-bold text-bw-70">{t('previousSessions')}</div>;
}
