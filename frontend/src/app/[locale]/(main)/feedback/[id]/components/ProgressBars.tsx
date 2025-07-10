import SegmentedProgress from '@/components/ui/SegmentedProgress';
import { useEffect, useState } from 'react';

function AnimatedProgressBar({ label, value }: { label: string; value: number }) {
  const [animatedValue, setAnimatedValue] = useState(0);
  useEffect(() => {
    setAnimatedValue(0);
    if (value > 0) {
      const current = 0;
      const interval = setInterval(() => {
        setAnimatedValue(current + 1);
        if (current >= value) clearInterval(interval);
      }, 400);
      return () => clearInterval(interval);
    }
    return undefined;
  }, [value]);
  return (
    <div className="flex flex-col gap-1">
      <span className="text-lg">{label}</span>
      <SegmentedProgress className="w-full" value={animatedValue} />
    </div>
  );
}

interface ProgressBarItem {
  key: string;
  value: number;
}

interface ProgressBarsProps {
  data: ProgressBarItem[];
}

export default function ProgressBars({ data }: ProgressBarsProps) {
  return (
    <div className="flex flex-col gap-8 flex-1 w-full p-2">
      {data.map((item) => (
        <AnimatedProgressBar key={item.key} label={item.key} value={item.value} />
      ))}
    </div>
  );
}
