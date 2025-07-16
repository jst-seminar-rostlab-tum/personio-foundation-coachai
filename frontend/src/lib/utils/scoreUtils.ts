export const calculateAverageScore = (scoreSum: number, totalSessions: number): string => {
  if (
    totalSessions === 0 ||
    scoreSum === 0 ||
    Number.isNaN(scoreSum) ||
    Number.isNaN(totalSessions)
  )
    return '-';

  const averageScorePercentage = Math.round(scoreSum / totalSessions);
  const averageScore = averageScorePercentage.toFixed(1);

  return averageScore;
};
