'use client';

import * as React from 'react';
import * as AvatarPrimitive from '@radix-ui/react-avatar';

import { cn } from '@/lib/utils/cnMerge';

/**
 * Wrapper for the Radix avatar root.
 */
function Avatar({ className, ...props }: React.ComponentProps<typeof AvatarPrimitive.Root>) {
  return (
    <AvatarPrimitive.Root
      data-slot="avatar"
      className={cn(
        'relative flex size-10 text-lg shrink-0 overflow-hidden rounded-full',
        className
      )}
      {...props}
    />
  );
}

/**
 * Image slot for the avatar.
 */
function AvatarImage({ className, ...props }: React.ComponentProps<typeof AvatarPrimitive.Image>) {
  return (
    <AvatarPrimitive.Image
      data-slot="avatar-image"
      className={cn('aspect-square size-full', className)}
      {...props}
    />
  );
}

/**
 * Fallback slot for the avatar.
 */
function AvatarFallback({
  className,
  ...props
}: React.ComponentProps<typeof AvatarPrimitive.Fallback>) {
  return (
    <AvatarPrimitive.Fallback
      data-slot="avatar-fallback"
      className={cn(
        'bg-bw-40 text-bw-70 flex size-full items-center justify-center rounded-full',
        className
      )}
      {...props}
    />
  );
}

export { Avatar, AvatarImage, AvatarFallback };
