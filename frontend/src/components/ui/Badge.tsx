import * as React from 'react';
import { Slot } from '@radix-ui/react-slot';
import { cva, type VariantProps } from 'class-variance-authority';

import { cn } from '@/lib/utils/cnMerge';

const badgeVariants = cva(
  'inline-flex items-center justify-center rounded-[100px] border px-3 py-1 text-xs font-medium w-fit whitespace-nowrap shrink-0 [&>svg]:size-3 gap-1 [&>svg]:pointer-events-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] aria-invalid:ring-flame-50/20 aria-invalid:border-flame-50 transition-[color,box-shadow] overflow-hidden',
  {
    variants: {
      variant: {
        default: 'border-transparent bg-marigold-10 text-marigold-90 [a&]:hover:bg-primary/90',
        outline:
          'border-marigold-30 text-marigold-90 [a&]:hover:bg-accent [a&]:hover:text-accent-foreground',
        easy: 'border-transparent bg-forest-10 text-forest-90',
        medium: 'border-transparent bg-marigold-10 text-marigold-90',
        hard: 'border-transparent bg-flame-5 text-flame-90',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  }
);

interface BadgeProps extends React.ComponentProps<'span'>, VariantProps<typeof badgeVariants> {
  asChild?: boolean;
}

function Badge({ className, variant, asChild = false, ...props }: BadgeProps) {
  const Comp = asChild ? Slot : 'span';

  return (
    <Comp data-slot="badge" className={cn(badgeVariants({ variant }), className)} {...props} />
  );
}

export { Badge, badgeVariants };
