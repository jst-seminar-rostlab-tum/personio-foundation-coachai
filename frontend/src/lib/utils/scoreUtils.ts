export const calculateAverageScore = (scoreSum: number, totalSessions: number): string => {
  if (
    totalSessions === 0 ||
    scoreSum === 0 ||
    Number.isNaN(scoreSum) ||
    Number.isNaN(totalSessions)
  )
    return '-';

  const averageScorePercentage = Math.round(scoreSum / totalSessions);
  const averageScore = ((averageScorePercentage / 100) * 5).toFixed(1);

  return averageScore;
};
