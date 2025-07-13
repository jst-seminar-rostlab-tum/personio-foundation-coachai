import StatCard from '@/components/common/StatCard';
import { UserStatsResponse } from '@/interfaces/models/UserStats';
import { getTranslations } from 'next-intl/server';
import SegmentedProgress from '@/components/ui/SegmentedProgress';

export default async function HistoryStats({ stats }: UserStatsResponse) {
  const t = await getTranslations('History');
  const tCommon = await getTranslations('Common');

  return (
    <div className="w-full">
      <div className="w-full flex flex-col gap-8">
        <div className="flex-1">
          <div className="text-md mb-4 text-bw-70">{t('skillsPerformance')}</div>
          <div className="flex flex-col gap-16 sm:grid sm:grid-cols-2 sm:gap-y-8 px-2">
            {Object.entries(stats.skillsPerformance).map(([key], idx) => (
              <div key={key} className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm text-bw-70">{tCommon(key)}</span>
                </div>
                <SegmentedProgress className="w-full" value={2 + (idx % 4)} />
              </div>
            ))}
          </div>
        </div>

        <div className="mt-10">
          <div className="text-md mb-4">{t('statistics')}</div>
          <div className="flex flex-row gap-2 md:gap-6 min-w-0 overflow-x-auto">
            <StatCard value={stats.totalSessions} label={tCommon('totalSessions')} />
            <StatCard value={`${stats.averageScore ?? 0}%`} label={tCommon('avgScore')} />
            <StatCard value={stats.goalsAchieved} label={tCommon('goalsAchieved')} />
          </div>
        </div>
      </div>
    </div>
  );
}
