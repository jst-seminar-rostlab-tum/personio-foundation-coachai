'use client';

import { Toaster as Sonner, ToasterProps } from 'sonner';

const Toaster = ({ ...props }: ToasterProps) => {
  return (
    <Sonner
      className="toaster group"
      style={
        {
          '--normal-bg': 'var(--bw-50)',
          '--normal-text': 'var(--foreground)',
          '--normal-border': 'var(--bw-70)',
        } as React.CSSProperties
      }
      {...props}
    />
  );
};

export { Toaster };
