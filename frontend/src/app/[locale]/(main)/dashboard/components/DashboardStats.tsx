'use client';

import { useTranslations } from 'next-intl';
import StatCard from '@/components/common/StatCard';
import useUserStats from '@/services/useUserStats';

export default function DashboardStats() {
  const t = useTranslations('Dashboard');

  const userId = '763c76f3-e5a4-479c-8b53-e3418d5e2ef5';
  const { data, error } = useUserStats(userId);

  if (error) return <p className="text-red-500">{error}</p>;
  if (!data) return null;

  return (
    <>
      {data && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard value={data.totalSessions} label={t('userStats.totalSessions')} />
          <StatCard value={`${data.trainingTime}h`} label={t('userStats.trainingTime')} />
          <StatCard value={`${data.currentStreakDays}d`} label={t('userStats.currentStreak')} />
          <StatCard value={`${data.averageScore}%`} label={t('userStats.avgScore')} />
        </div>
      )}
    </>
  );
}
