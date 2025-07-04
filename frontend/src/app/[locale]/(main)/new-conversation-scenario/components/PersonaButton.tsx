import React from 'react';

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
      className={`${personaButtonStyles}${selected ? ' outline-none bg-marigold-30' : ''}${className ? ` ${className}` : ''}`}
      onClick={onClick}
    >
      {children}
    </button>
  );
}
