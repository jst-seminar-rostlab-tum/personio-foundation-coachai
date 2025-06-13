import { useTranslations } from 'next-intl';
import Progress from '@/components/ui/Progress';
import StatCard from '@/components/common/StatCard';

const mockStats = [
  { key: 'structure', value: 85 },
  { key: 'empathy', value: 70 },
  { key: 'solutionFocus', value: 75 },
  { key: 'clarity', value: 90 },
];

export default function HistoryStats() {
  const t = useTranslations('History');
  return (
    <div className="w-full px-4">
      <div className="w-full flex flex-col  gap-6">
        <div className="flex-1">
          <div className="text-xl mb-4 text-bw-70">{t('skillsPerformance')}</div>
          <div className="flex flex-col gap-6 lg:grid lg:grid-cols-2 lg:gap-y-8 px-2">
            {mockStats.map((stat) => (
              <div key={stat.key} className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm text-bw-70 ">{t(stat.key)}</span>
                  <span className="text-sm text-bw-70">{stat.value}%</span>
                </div>
                <Progress value={stat.value} className="w-full" />
              </div>
            ))}
          </div>
        </div>

        <div className="mt-10">
          <div className="text-xl mb-4">{t('activity')}</div>
          <div className="flex flex-row gap-2 md:gap-6 min-w-0 overflow-x-auto">
            <StatCard value={12} label={t('totalSessions')} />
            <StatCard value={'82%'} label={t('avgScore')} />
            <StatCard value={4} label={t('goalsAchieved')} />
          </div>
        </div>
      </div>
    </div>
  );
}
