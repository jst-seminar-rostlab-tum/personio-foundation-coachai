import React from 'react';
import { cn } from '@/lib/utils';

interface PersonaButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  selected?: boolean;
  className?: string;
}

const personaButtonStyles =
  'w-full box-border rounded-2xl flex flex-col items-center justify-center text-lg outline outline-2 outline-bw-20 cursor-pointer hover:bg-marigold-30/80 active:outline-none active:bg-marigold-30 disabled:pointer-events-none p-4';

export function PersonaButton({ children, selected, onClick, className }: PersonaButtonProps) {
  return (
    <button
      type="button"
      className={cn(personaButtonStyles, { 'outline-none bg-marigold-30': selected }, className)}
      onClick={onClick}
    >
      {children}
    </button>
  );
}
