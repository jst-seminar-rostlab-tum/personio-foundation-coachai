import * as React from 'react';
import { Slot } from '@radix-ui/react-slot';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const buttonVariants = cva('text-lg font-medium cursor-pointer disabled:pointer-events-none', {
  variants: {
    variant: {
      default: 'bg-marigold-30 text-marigold-95',
      secondary: 'bg-transparent border-1 border-solid border-bw-20 text-bw-70',
      disabled: 'bg-bw-10 text-bw-40',
    },
    size: {
      default: 'rounded-md px-4 py-3',
    },
  },
  defaultVariants: {
    variant: 'default',
    size: 'default',
  },
});

function Button({
  className,
  variant,
  size,
  asChild = false,
  ...props
}: React.ComponentProps<'button'> &
  VariantProps<typeof buttonVariants> & {
    asChild?: boolean;
  }) {
  const Comp = asChild ? Slot : 'button';

  return (
    <Comp
      data-slot="button"
      className={cn(buttonVariants({ variant, size, className }))}
      {...props}
    />
  );
}

export { Button, buttonVariants };
