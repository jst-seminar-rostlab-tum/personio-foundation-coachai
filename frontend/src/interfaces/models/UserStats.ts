import { SessionScores } from './Common';

/**
 * Aggregated stats for a user.
 */
export type UserStats = {
  totalSessions: number;
  trainingTime: number;
  currentStreakDays: number;
  averageScore: number;
  goalsAchieved: number;
  performanceOverTime: number[];
  skillsPerformance: SessionScores;
  dailySessionLimit: number;
  numRemainingDailySessions: number;
};

/**
 * Response wrapper for user stats.
 */
export type UserStatsResponse = {
  stats: UserStats;
};
