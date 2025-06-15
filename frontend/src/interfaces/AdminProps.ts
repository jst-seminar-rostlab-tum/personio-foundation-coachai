export interface AdminProps {
  stats: Promise<{
    total_users: number;
    total_trainings: number;
    total_reviews: number;
    average_score: number;
  }>;
}
