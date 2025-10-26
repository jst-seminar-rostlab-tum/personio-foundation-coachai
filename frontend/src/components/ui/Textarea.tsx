import * as React from 'react';

import { cn } from '@/lib/utils/cnMerge';

function Textarea({ className, ...props }: React.ComponentProps<'textarea'>) {
  return (
    <textarea
      data-slot="textarea"
      className={cn(
        'border border-bw-40 placeholder:text-muted-foreground aria-invalid:ring-flame-50/20 dark:aria-invalid:ring-flame-50/40 aria-invalid:border-flame-50 dark:bg-input/30 flex field-sizing-content min-h-16 w-full rounded-md bg-custom-beige px-3 py-2 shadow-xs transition-[color,box-shadow] outline-none focus:outline-none focus:ring-2 focus:ring-bw-40 focus:ring-offset-2 disabled:cursor-not-allowed disabled:text-bw-70',
        className
      )}
      {...props}
    />
  );
}

export { Textarea };
