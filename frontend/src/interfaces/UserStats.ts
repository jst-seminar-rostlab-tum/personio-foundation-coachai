type SkillsPerformance = {
  structure: number;
  empathy: number;
  solutionFocus: number;
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
