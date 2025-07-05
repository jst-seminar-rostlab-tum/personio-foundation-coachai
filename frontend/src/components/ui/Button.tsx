import * as React from 'react';
import { Slot } from '@radix-ui/react-slot';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils/cnMerge';

const buttonVariants = cva(
  'text-lg font-medium cursor-pointer inline-flex items-center justify-center gap-2 max-h-10 disabled:pointer-events-none [&_svg]:pointer-events-none [&_svg:not([class*="size-"])]:size-4 shrink-0 [&_svg]:shrink-0',
  {
    variants: {
      variant: {
        default: 'bg-marigold-30 text-marigold-95 hover:bg-marigold-30/80',
        secondary: 'bg-bw-60 text-white hover:bg-bw-60/80',
        outline:
          'bg-transparent outline-1 outline-solid outline-bw-20 text-bw-70 hover:outline-2 hover:outline-bw-70',
        disabled: 'bg-bw-10 text-bw-40',
        destructive: 'bg-flame-50 text-white shadow-xs hover:bg-flame-50/80',
        ghost: 'hover:bg-bw-10',
        link: 'text-blue-600 underline hover:text-blue-800',
      },
      size: {
        default: 'rounded-md px-4 py-3',
        full: 'rounded-md px-4 py-3 w-full justify-center flex-1',
        pagination: 'h-9 px-4 py-2 has-[>svg]:px-3 hover:bg-bw-10 hover:rounded-md',
        paginationIcon: 'size-9 rounded-md ',
        iconLarge:
          'w-14 h-14 max-h-14 aspect-square rounded-full flex items-center justify-center p-0',
        icon: 'rounded-full p-2',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
);

function Button({
  className,
  variant,
  size,
  asChild = false,
  disabled = false,
  ...props
}: React.ComponentProps<'button'> &
  VariantProps<typeof buttonVariants> & {
    asChild?: boolean;
    disabled?: boolean;
  }) {
  const Comp = asChild ? Slot : 'button';

  return (
    <Comp
      data-slot="button"
      className={cn(buttonVariants({ variant, size, className }))}
      disabled={disabled || variant === 'disabled'}
      {...props}
    />
  );
}

export { Button, buttonVariants };
