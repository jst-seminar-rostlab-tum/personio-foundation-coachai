import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { X } from 'lucide-react'; // <-- Add this

function cn(...classes) {
  return classes.filter(Boolean).join(' ');
}

const alertVariants = cva(
  'bg-background relative w-full max-w-md sm:max-w-lg mx-auto rounded-lg border px-4 py-3 text-base grid has-[>svg]:grid-cols-[calc(var(--spacing)*4)_1fr] grid-cols-[0_1fr] has-[>svg]:gap-x-3 gap-y-0.5 items-start [&>svg]:size-4 [&>svg]:translate-y-0.5 [&>svg]:text-current shadow',
  {
    variants: {
      variant: {
        default: 'text-foreground',
        destructive: 'text-destructive',
      },
    },
    defaultVariants: {
      variant: 'destructive',
    },
  }
);

function Alert({
  className,
  variant,
  children,
  ...props
}: React.ComponentProps<'div'> & VariantProps<typeof alertVariants>) {
  const [open, setOpen] = React.useState(true);

  if (!open) return null;

  return (
    <div className="fixed bottom-4 left-4 right-4 sm:left-8 sm:right-8 z-50 pointer-events-none">
      <div
        data-slot="alert"
        role="alert"
        className={cn(alertVariants({ variant }), 'relative pointer-events-auto', className)}
        {...props}
      >
        {children}
        <button
          onClick={() => setOpen(false)}
          className="absolute right-2 top-1/2 -translate-y-1/2 p-1 cursor-pointer"
          aria-label="Close"
        >
          <X className="w-5 h-5 text-muted-foreground hover:text-foreground" />
        </button>
      </div>
    </div>
  );
}

function AlertTitle({ className, ...props }: React.ComponentProps<'div'>) {
  return (
    <div
      data-slot="alert-title"
      className={cn('col-start-2 line-clamp-1 min-h-4 tracking-tight text-lg', className)}
      {...props}
    />
  );
}

function AlertDescription({ className, ...props }: React.ComponentProps<'div'>) {
  return (
    <div
      data-slot="alert-description"
      className={cn(
        'col-start-2 grid justify-items-start gap-1 [&_p]:leading-relaxed text-base',
        className
      )}
      {...props}
    />
  );
}

export { Alert, AlertTitle, AlertDescription };
