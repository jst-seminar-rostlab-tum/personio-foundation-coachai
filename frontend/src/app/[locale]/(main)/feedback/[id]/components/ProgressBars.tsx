import SegmentedProgress from '@/components/ui/SegmentedProgress';
import { useEffect, useState } from 'react';

/**
 * Represents a single labeled progress bar.
 */
interface ProgressBarItem {
  key: string;
  value: number;
}

/**
 * Props for rendering a list of progress bars.
 */
interface ProgressBarsProps {
  data: ProgressBarItem[];
}

/**
 * Renders a single animated progress bar with label.
 */
function AnimatedProgressBar({ label, value }: { label: string; value: number }) {
  const [animatedValue, setAnimatedValue] = useState(0);

  useEffect(() => {
    setAnimatedValue(0);
    if (value > 0) {
      const interval = setInterval(() => {
        setAnimatedValue((prev) => {
          if (prev + 1 >= value) {
            clearInterval(interval);
            return value;
          }
          return prev + 1;
        });
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

/**
 * Displays a set of progress bars for feedback scores.
 */
export default function ProgressBars({ data }: ProgressBarsProps) {
  return (
    <div className="flex flex-col gap-8 flex-1 w-full p-2">
      {data.map((item) => (
        <AnimatedProgressBar key={item.key} label={item.key} value={item.value} />
      ))}
    </div>
  );
}
