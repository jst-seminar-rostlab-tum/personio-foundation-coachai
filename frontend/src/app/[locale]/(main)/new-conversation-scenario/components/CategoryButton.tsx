'use client';

import { cn } from '@/lib/utils/cnMerge';
import { ButtonHTMLAttributes } from 'react';

interface CategoryButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  selected?: boolean;
  children?: React.ReactNode;
}

const buttonStyles =
  'rounded-2xl flex flex-col items-center justify-center text-lg outline outline-2 outline-bw-20 cursor-pointer hover:bg-marigold-30/80 active:outline-none active:bg-marigold-30 disabled:pointer-events-none p-8 group';

function CategoryButton({ className, selected, children, ...props }: CategoryButtonProps) {
  let image = null;
  let title = null;
  let description = null;

  if (Array.isArray(children)) {
    [image, title, description] = children;
  } else {
    image = children;
    title = null;
    description = null;
  }

  return (
    <button
      data-slot="button"
      className={cn(buttonStyles, selected ? 'outline-none bg-marigold-30' : '', className || '')}
      {...props}
    >
      <div className="flex flex-col items-center w-full h-full">
        <div className="flex justify-center w-full mb-2">{image}</div>
        <div className="flex flex-col w-full text-left gap-2 mt-1">
          <span className="text-xl text-bw-70 font-semibold">{title}</span>
          {description && (
            <span
              className={`text-base leading-relaxed text-bw-40 group-hover:text-bw-70 ${
                selected ? 'text-bw-70' : ''
              }`}
            >
              {description}
            </span>
          )}
        </div>
      </div>
    </button>
  );
}

export { CategoryButton };
