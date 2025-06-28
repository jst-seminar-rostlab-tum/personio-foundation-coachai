import { useTranslations } from 'next-intl';
import StatCard from '@/components/common/StatCard';
import { UserStatsResponse } from '@/interfaces/models/UserStats';
import { use } from 'react';

export default function DashboardStats({ stats }: UserStatsResponse) {
  const t = useTranslations('Dashboard');
  const data = use(stats);

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard value={data.totalSessions} label={t('userStats.totalSessions')} />
      <StatCard value={`${data.trainingTime.toFixed(1)}h`} label={t('userStats.trainingTime')} />
      <StatCard value={`${data.currentStreakDays}d`} label={t('userStats.currentStreak')} />
      <StatCard value={`${data.averageScore}%`} label={t('userStats.avgScore')} />
    </div>
  );
}
