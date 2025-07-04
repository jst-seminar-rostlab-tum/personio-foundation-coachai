import { SessionScores } from './Common';

export type UserStats = {
  totalSessions: number;
  trainingTime: number;
  currentStreakDays: number;
  averageScore: number;
  goalsAchieved: number;
  performanceOverTime: number[];
  skillsPerformance: SessionScores;
};

export type UserStatsResponse = {
  stats: UserStats;
};
