export interface AdminProps {
  stats: Promise<{
    totalUsers: number;
    totalTrainings: number;
    totalReviews: number;
    averageScore: number;
    dailyTokenLimit: number;
  }>;
}
