'use client';

import { useTranslations } from 'next-intl';
import Progress from '@/components/ui/Progress';
import StatCard from '@/components/common/StatCard';
import useUserStats from '@/services/useUserStats';

export default function HistoryStats() {
  const t = useTranslations('History');

  const userId = '763c76f3-e5a4-479c-8b53-e3418d5e2ef5';
  const { data, error } = useUserStats(userId);

  if (error) return <p className="text-red-500">{error}</p>;
  if (!data) return null;

  return (
    <div className="w-full px-4">
      <div className="w-full flex flex-col  gap-6">
        <div className="flex-1">
          <div className="text-xl mb-4 text-bw-70">{t('skillsPerformance')}</div>
          <div className="flex flex-col gap-6 lg:grid lg:grid-cols-2 lg:gap-y-8 px-2">
            {Object.entries(data.skillsPerformance).map(([key, value]) => (
              <div key={key} className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm text-bw-70">{t(key)}</span>
                  <span className="text-sm text-bw-70">{value}%</span>
                </div>
                <Progress value={value} className="w-full" />
              </div>
            ))}
          </div>
        </div>

        <div className="mt-10">
          <div className="text-xl mb-4">{t('activity')}</div>
          <div className="flex flex-row gap-2 md:gap-6 min-w-0 overflow-x-auto">
            {data && (
              <>
                <StatCard value={data.totalSessions} label={t('totalSessions')} />
                <StatCard value={`${data.averageScore}%`} label={t('avgScore')} />
                <StatCard value={data.goalsAchieved} label={t('goalsAchieved')} />
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
