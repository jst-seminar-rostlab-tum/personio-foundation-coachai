'use client';

import React from 'react';

interface CategoryButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  selected?: boolean;
  children?: React.ReactNode;
}

const buttonStyles =
  'rounded-2xl flex flex-col items-center justify-center text-lg outline outline-2 outline-bw-20 cursor-pointer hover:bg-marigold-30/80 active:outline-none active:bg-marigold-30 disabled:pointer-events-none p-12 group';

function CategoryButton({ className, selected, children, ...props }: CategoryButtonProps) {
  // Support for children as an array: [image, title, description]
  let image = null;
  let title = null;
  let description = null;

  if (Array.isArray(children)) {
    // Expect: [image, title, description]
    [image, title, description] = children;
  } else if (children && typeof children === 'object') {
    image = children;
    title = null;
    description = null;
  }

  return (
    <button
      data-slot="button"
      className={[
        buttonStyles,
        selected ? 'outline-none bg-marigold-30' : '',
        className || '',
      ].join(' ')}
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
