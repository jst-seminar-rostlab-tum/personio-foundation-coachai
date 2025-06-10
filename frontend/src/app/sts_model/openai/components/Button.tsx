import { ReactNode, MouseEventHandler } from 'react';

type ButtonProps = {
  icon?: ReactNode;
  children: ReactNode;
  onClick?: MouseEventHandler<HTMLButtonElement>;
  className?: string;
};

export default function Button({ icon, children, onClick, className = '' }: ButtonProps) {
  return (
    <button
      className={`bg-gray-800 text-white rounded-full p-4 flex items-center gap-1 hover:opacity-90 ${className}`}
      onClick={onClick}
    >
      {icon}
      {children}
    </button>
  );
}
