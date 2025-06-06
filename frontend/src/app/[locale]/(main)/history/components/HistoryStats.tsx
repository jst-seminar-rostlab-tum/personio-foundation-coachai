import { useTranslations } from 'next-intl';
import Progress from '@/components/ui/Progress';

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
          <div className="flex flex-col gap-6 lg:flex-row lg:gap-8 px-2">
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
            <div className="flex-1 min-w-0 bg-bw-20 rounded px-2 py-2 flex flex-row items-center justify-between">
              <span className="text-2xl font-semibold text-bw-70">12</span>
              <span className="text-xs text-bw-70 leading-tight truncate whitespace-pre-line">
                {t('totalSessions')}
              </span>
            </div>
            <div className="flex-1 min-w-0 bg-bw-20 rounded px-2 py-2 flex flex-row items-center justify-between">
              <span className="text-2xl font-semibold text-bw-70">
                82<span className="text-sm text-bw-70">%</span>
              </span>
              <span className="text-xs text-bw-70 leading-tight truncate whitespace-pre-line">
                {t('avgScore')}
              </span>
            </div>
            <div className="flex-1 min-w-0 bg-bw-20 rounded px-2 py-2 flex flex-row items-center justify-between">
              <span className="text-2xl font-semibold text-bw-70">4</span>
              <span className="text-xs text-bw-70 leading-tight truncate whitespace-pre-line">
                {t('goalsAchieved')}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
