/**
 * Calculates a formatted average score or returns a placeholder when invalid.
 */
export const calculateAverageScore = (scoreSum: number, totalSessions: number): string => {
  if (
    totalSessions === 0 ||
    scoreSum === 0 ||
    Number.isNaN(scoreSum) ||
    Number.isNaN(totalSessions)
  )
    return '-';

  const averageScorePercentage = Math.round((scoreSum / totalSessions) * 10) / 10;
  const averageScore = averageScorePercentage.toFixed(1);

  return averageScore;
};
