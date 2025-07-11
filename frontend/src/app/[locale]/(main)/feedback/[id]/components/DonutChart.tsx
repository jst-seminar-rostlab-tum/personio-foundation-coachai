import { useEffect, useState } from 'react';

interface DonutChartProps {
  percent: number;
  goalsAchieved: number;
  goalsTotal: number;
  label: string;
}

const radius = 70;
const stroke = 8;
const normalizedRadius = radius;
const circumference = 2 * Math.PI * normalizedRadius;

export default function DonutChart({ percent, goalsAchieved, goalsTotal, label }: DonutChartProps) {
  const [animatedPercent, setAnimatedPercent] = useState(0);
  const [animatedNumber, setAnimatedNumber] = useState(0);

  useEffect(() => {
    const duration = 1000;
    const startValue = Math.max(percent - 10, 0);
    let chartStart = 0;
    let numberStart = 0;

    const easeInOutCubic = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - (-2 * t + 2) ** 3 / 2);

    function animateChartFill(now: number) {
      if (!chartStart) chartStart = now;
      const elapsed = now - chartStart;
      const progress = Math.min(elapsed / duration, 1);
      const eased = easeInOutCubic(progress);
      setAnimatedPercent(Math.round(percent * eased));
      if (progress < 1) {
        requestAnimationFrame(animateChartFill);
      }
    }
    function animateNumber(now: number) {
      if (!numberStart) numberStart = now;
      const elapsed = now - numberStart;
      const progress = Math.min(elapsed / duration, 1);
      setAnimatedNumber(Math.round(startValue + (percent - startValue) * progress));
      if (progress < 1) {
        requestAnimationFrame(animateNumber);
      }
    }
    setAnimatedPercent(0);
    setAnimatedNumber(startValue);
    requestAnimationFrame(animateChartFill);
    requestAnimationFrame(animateNumber);
  }, [percent]);

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
            className="stroke-bw-20"
          />
          <circle
            cx="80"
            cy="80"
            r={radius}
            fill="none"
            strokeWidth={stroke}
            className="stroke-marigold-50"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            transform="rotate(-90 80 80)"
          />
        </svg>
        <div
          className="absolute top-1/2 left-1/2 flex flex-col items-center justify-center w-full gap-2"
          style={{ transform: 'translate(-50%, -50%)' }}
        >
          <span className="font-medium text-5xl fill-bw-60 text-bw-60">{animatedNumber}%</span>
          <span className="text-base text-bw-40 mt-1 flex items-baseline gap-1.5">
            <span className="text-xl font-semibold">
              {goalsAchieved}/{goalsTotal}
            </span>
            {label}
          </span>
        </div>
      </div>
    </div>
  );
}
