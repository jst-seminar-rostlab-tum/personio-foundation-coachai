type SkillsPerformance = {
  structure: number;
  empathy: number;
  focus: number;
  clarity: number;
};

export type UserStats = {
  totalSessions: number;
  trainingTime: number;
  currentStreakDays: number;
  averageScore: number;
  goalsAchieved: number;
  performanceOverTime: number[];
  skillsPerformance: SkillsPerformance;
};

export type UserStatsResponse = {
  stats: UserStats;
};
