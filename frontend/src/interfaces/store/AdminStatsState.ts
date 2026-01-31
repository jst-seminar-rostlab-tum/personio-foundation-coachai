/**
 * Store state for admin statistics.
 */
export interface AdminStatsState {
  stats: {
    totalUsers: number;
    totalTrainings: number;
    totalReviews: number;
    scoreSum: number;
  };
  setStats: (stats: AdminStatsState['stats']) => void;
}
