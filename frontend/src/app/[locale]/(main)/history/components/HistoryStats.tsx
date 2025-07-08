import Progress from '@/components/ui/Progress';
import StatCard from '@/components/common/StatCard';
import { UserStatsResponse } from '@/interfaces/models/UserStats';
import { getTranslations } from 'next-intl/server';

export default async function HistoryStats({ stats }: UserStatsResponse) {
  const t = await getTranslations('History');
  const tCommon = await getTranslations('Common');

  return (
    <div className="w-full">
      <div className="w-full flex flex-col  gap-6">
        <div className="flex-1">
          <div className="text-xl mb-4 text-bw-70">{t('skillsPerformance')}</div>
          <div className="flex flex-col gap-6 lg:grid lg:grid-cols-2 lg:gap-y-8 px-2">
            {Object.entries(stats.skillsPerformance).map(([key, value]) => (
              <div key={key} className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm text-bw-70">{tCommon(key)}</span>
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
            <StatCard value={stats.totalSessions} label={tCommon('totalSessions')} />
            <StatCard value={`${stats.averageScore}%`} label={tCommon('avgScore')} />
            <StatCard value={stats.goalsAchieved} label={tCommon('goalsAchieved')} />
          </div>
        </div>
      </div>
    </div>
  );
}
