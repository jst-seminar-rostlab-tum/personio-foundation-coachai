import { cn } from '@/lib/utils';
import { ButtonHTMLAttributes } from 'react';

interface CategoryButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  selected?: boolean;
  children?: React.ReactNode;
}

const buttonStyles =
  'rounded-2xl flex flex-col items-center justify-center text-lg outline outline-2 outline-bw-20 cursor-pointer hover:bg-marigold-30/80 active:outline-none active:bg-marigold-30 disabled:pointer-events-none p-12';

function CategoryButton({ className, selected, children, ...props }: CategoryButtonProps) {
  // Support for children as an array: [image, title, description]
  let image = null;
  let title = null;
  let description = null;

  if (Array.isArray(children)) {
    // Expect: [image, title, description]
    [image, title, description = 'This is a short description of the scenario.'] = children;
  } else if (children && typeof children === 'object') {
    image = children;
    title = null;
    description = 'This is a short description of the scenario.';
  }

  return (
    <button
      data-slot="button"
      className={cn(
        buttonStyles,
        {
          'outline-none bg-marigold-30': selected,
        },
        className
      )}
      {...props}
    >
      <div className="flex flex-col items-center w-full h-full">
        <div className="flex justify-center w-full mb-2">{image}</div>
        <div className="flex flex-col w-full text-left gap-2 mt-1">
          <span className="text-xl text-bw-70 font-semibold">{title}</span>
          <span className={cn('text-base leading-relaxed', selected ? 'text-bw-70' : 'text-bw-40')}>
            {description}
          </span>
        </div>
      </div>
    </button>
  );
}

export { CategoryButton };
