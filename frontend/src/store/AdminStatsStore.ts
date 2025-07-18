import { AdminStatsState } from '@/interfaces/store/AdminStatsState';
import { create } from 'zustand';

export const useAdminStatsStore = create<AdminStatsState>()((set) => ({
  stats: {
    totalUsers: 0,
    totalTrainings: 0,
    totalReviews: 0,
    scoreSum: 0,
  },
  setStats: (stats) => set({ stats }),
}));
