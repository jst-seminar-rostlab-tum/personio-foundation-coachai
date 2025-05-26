import { cn } from '@/lib/utils';
import { ButtonHTMLAttributes } from 'react';

interface CategoryButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  selected?: boolean;
}

const buttonStyles =
  'w-[160px] h-[160px] rounded-2xl flex flex-col items-center justify-center text-lg outline outline-2 outline-bw-20 cursor-pointer hover:bg-marigold-30/80 active:outline-none active:bg-marigold-30 disabled:pointer-events-none';

function CategoryButton({ className, selected, ...props }: CategoryButtonProps) {
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
    />
  );
}

export { CategoryButton };
