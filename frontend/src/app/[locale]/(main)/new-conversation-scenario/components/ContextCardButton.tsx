import { ButtonHTMLAttributes } from 'react';

interface ContextCardButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  selected: boolean;
  label: string;
  subtitle: string;
  onClick: () => void;
}

export default function ContextCardButton({
  selected,
  label,
  subtitle,
  onClick,
  ...props
}: ContextCardButtonProps) {
  return (
    <button
      type="button"
      className={`w-full md:w-1/2 box-border rounded-2xl flex flex-col items-start justify-center text-lg outline outline-2 outline-bw-20 cursor-pointer hover:bg-marigold-30/80 active:outline-none active:bg-marigold-30 disabled:pointer-events-none p-6 group ${selected ? 'outline-none bg-marigold-30' : ''}`}
      onClick={onClick}
      {...props}
    >
      <span className="text-xl text-bw-70 font-semibold mb-2 text-left">{label}</span>
      <span
        className={`text-base leading-relaxed text-bw-40 group-hover:text-bw-70 ${selected ? 'text-bw-70' : ''} text-left`}
      >
        {subtitle}
      </span>
    </button>
  );
}
