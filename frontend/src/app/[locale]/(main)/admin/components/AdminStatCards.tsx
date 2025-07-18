'use client';

import { adminService } from '@/services/AdminService';
import StatCard from '@/components/common/StatCard';
import { useTranslations } from 'next-intl';
import { api } from '@/services/ApiClient';
import { calculateAverageScore } from '@/lib/utils/scoreUtils';
import { useAdminStatsStore } from '@/store/AdminStatsStore';
import { useEffect } from 'react';

export default function AdminStatCards() {
  const t = useTranslations('Admin');
  const tCommon = useTranslations('Common');

  const { stats, setStats } = useAdminStatsStore();

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await adminService.getAdminStats(api);
        setStats(data);
      } catch (error) {
        console.error('Error fetching stats:', error);
      }
    };
    fetchStats();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const averageScore = calculateAverageScore(stats.scoreSum, stats.totalTrainings);

  const statsArray = [
    { value: stats.totalUsers, label: t('statActiveUsers') },
    { value: stats.totalTrainings, label: tCommon('totalSessions') },
    { value: stats.totalReviews, label: tCommon('reviews') },
    { value: `${averageScore}/20`, label: tCommon('avgScore') },
  ];

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      {statsArray.map((stat, i) => (
        <StatCard key={i} value={stat.value} label={stat.label} />
      ))}
    </div>
  );
}
