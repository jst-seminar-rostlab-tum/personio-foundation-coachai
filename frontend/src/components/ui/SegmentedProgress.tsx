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
        return (
          <div
            key={i}
            className={cn(
              'flex-1 transition-colors',
              value > i ? 'bg-marigold-50' : 'bg-bw-20',
              rounded
            )}
          />
        );
      })}
    </div>
  );
}

export default SegmentedProgress;
