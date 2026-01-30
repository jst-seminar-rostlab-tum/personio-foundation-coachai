import { useEffect, useState } from 'react';

/**
 * Props for the animated score donut chart.
 */
interface DonutChartProps {
  totalScore: number;
  maxScore: number;
}

const radius = 70;
const stroke = 8;
const normalizedRadius = radius;
const circumference = 2 * Math.PI * normalizedRadius;

/**
 * Renders an animated donut chart with score and total.
 */
export default function DonutChart({ totalScore, maxScore }: DonutChartProps) {
  const percent = maxScore > 0 ? (totalScore / maxScore) * 100 : 0;
  const [animatedPercent, setAnimatedPercent] = useState(0);
  const [animatedNumber, setAnimatedNumber] = useState(0);
  useEffect(() => {
    const duration = 1000;
    let start = 0;
    /**
     * Eases progress for smooth ring animation.
     */
    const easeInOutCubic = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - (-2 * t + 2) ** 3 / 2);
    /**
     * Animates the percentage ring and numeric score.
     */
    const animate = (now: number) => {
      if (!start) start = now;
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      const eased = easeInOutCubic(progress);
      setAnimatedPercent(percent * eased);
      setAnimatedNumber(Math.round(totalScore * progress));
      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };
    setAnimatedPercent(0);
    setAnimatedNumber(0);
    requestAnimationFrame(animate);
  }, [percent, totalScore]);
  const offset = circumference * (1 - animatedPercent / 100);

  return (
    <div className="flex items-center w-64 h-64 aspect-square max-w-xs flex-shrink-0 mx-auto md:mx-0">
      <div className="relative w-full h-full flex items-center justify-center">
        <svg className="w-full h-full" viewBox="0 0 160 160" aria-label="Overall Score Donut Chart">
          <circle
            cx="80"
            cy="80"
            r={radius}
            fill="none"
            strokeWidth={stroke}
            className="stroke-bw-40"
          />
          <circle
            cx="80"
            cy="80"
            r={radius}
            fill="none"
            strokeWidth={stroke}
            className="stroke-forest-90"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            transform="rotate(-90 80 80)"
          />
        </svg>
        <div
          className="absolute top-1/2 left-1/2 flex flex-col items-center justify-center w-full gap-1"
          style={{ transform: 'translate(-50%, -50%)' }}
        >
          <span>
            <span className="font-medium text-7xl fill-bw-60 text-bw-70">{animatedNumber}</span>
            <span className="font-regular text-5xl text-bw-70">/{maxScore}</span>
          </span>
        </div>
      </div>
    </div>
  );
}
