import * as React from 'react';

import { cn } from '@/lib/utils/cnMerge';

/**
 * Styled input control.
 */
function Input({ className, type, ...props }: React.ComponentProps<'input'>) {
  return (
    <input
      type={type}
      data-slot="input"
      className={cn(
        'file:text-base placeholder:text-muted-base border-input flex h-9 w-full min-w-0 rounded-md border border-bw-40 bg-custom-beige px-3 py-1 text-base shadow-xs transition-[color,box-shadow] outline-none file:inline-flex file:h-7 file:border-0 file:bg-custom-beige file:font-medium disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 md:text-base',
        'focus:outline-none focus:ring-2 focus:ring-bw-40 focus:ring-offset-2',
        'aria-invalid:ring-flame-50/20 aria-invalid:border-flame-50',
        'w-64 h-9',
        className
      )}
      {...props}
    />
  );
}

export default Input;
