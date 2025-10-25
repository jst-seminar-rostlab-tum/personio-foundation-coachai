import Image from 'next/image';

interface PersonaButtonProps {
  onClick?: () => void;
  selected?: boolean;
  className?: string;
  image: string;
  label: string;
}

const personaButtonStyles =
  'w-full box-border rounded-2xl flex flex-col items-center justify-center text-lg outline outline-2 outline-bw-40 cursor-pointer hover:bg-forest-90/80 hover:text-white active:outline-none active:bg-forest-90 disabled:pointer-events-none p-6';

export function PersonaButton({ selected, onClick, className, image, label }: PersonaButtonProps) {
  return (
    <button
      type="button"
      className={`${personaButtonStyles}${selected ? ' outline-none bg-forest-90 text-white' : ' text-black'}${className ? ` ${className}` : ''}`}
      onClick={onClick}
    >
      <div className="relative w-16 h-16 sm:w-20 sm:h-20 rounded-full overflow-hidden bg-custom-beige mb-3 flex-shrink-0 mx-auto">
        <Image src={image} alt={label} fill className="object-contain p-2 " />
      </div>
      <span className="text-md text-center">{label}</span>
    </button>
  );
}
