import Image from 'next/image';

interface PersonaButtonProps {
  onClick?: () => void;
  selected?: boolean;
  className?: string;
  image: string;
  label: string;
}

const personaButtonStyles =
  'w-full box-border rounded-2xl flex flex-col items-center justify-center text-lg outline outline-2 outline-bw-40 cursor-pointer hover:bg-marigold-30/80 active:outline-none active:bg-marigold-30 disabled:pointer-events-none p-6';

export function PersonaButton({ selected, onClick, className, image, label }: PersonaButtonProps) {
  return (
    <button
      type="button"
      className={`${personaButtonStyles}${selected ? ' outline-none bg-marigold-30' : ''}${className ? ` ${className}` : ''}`}
      onClick={onClick}
    >
      <div className="relative w-16 h-16 sm:w-20 sm:h-20 rounded-full overflow-hidden bg-white mb-3 flex-shrink-0 mx-auto">
        <Image src={image} alt={label} fill className="object-contain p-2 " />
      </div>
      <span className="text-md text-center">{label}</span>
    </button>
  );
}
