import * as React from 'react';
import { cn } from '@/lib/utils/cnMerge';

interface SegmentedProgressProps {
  className?: string;
  value: number; // 1-5
  max?: number; // default 5
}

function SegmentedProgress({ className, value, max = 5 }: SegmentedProgressProps) {
  return (
    <div className={cn('flex w-80 h-2 gap-0.5', className)}>
      {Array.from({ length: max }).map((_, i) => {
        let rounded = '';
        if (i === 0) rounded = 'rounded-l-full';
        else if (i === max - 1) rounded = 'rounded-r-full';
        // Calculate fill percent for this segment
        let fill = 0;
        if (value > i) {
          fill = value >= i + 1 ? 100 : (value - i) * 100;
        }
        return (
          <div key={i} className={cn('flex-1 bg-bw-20 relative overflow-hidden', rounded)}>
            <div
              className={cn(
                'absolute left-0 top-0 h-full bg-marigold-50 transition-all duration-500',
                rounded
              )}
              style={{ width: `${fill}%` }}
            />
          </div>
        );
      })}
    </div>
  );
}

export default SegmentedProgress;
