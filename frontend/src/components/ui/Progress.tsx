'use client';

import * as React from 'react';
import * as ProgressPrimitive from '@radix-ui/react-progress';

import { cn } from '@/lib/utils/cnMerge';

function Progress({
  className,
  value,
  ...props
}: React.ComponentProps<typeof ProgressPrimitive.Root>) {
  return (
    <ProgressPrimitive.Root
      data-slot="progress"
      className={cn('bg-bw-20 relative h-2 w-80 overflow-hidden rounded-full', className)}
      {...props}
    >
      <ProgressPrimitive.Indicator
        data-slot="progress-indicator"
        className="bg-marigold-40 h-full w-full flex-1 transition-all"
        style={{ transform: `translateX(-${100 - (value || 0)}%)` }}
      />
    </ProgressPrimitive.Root>
  );
}

export default Progress;
