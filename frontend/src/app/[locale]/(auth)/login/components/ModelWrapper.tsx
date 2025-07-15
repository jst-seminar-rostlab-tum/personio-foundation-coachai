'use client';

import { useRouter } from 'next/navigation';
import { ReactNode } from 'react';

interface ModalWrapperProps {
  children: ReactNode;
}

export function ModalWrapper({ children }: ModalWrapperProps) {
  const router = useRouter();

  const handleBackdropClick = () => {
    router.push('/login'); // You can preserve query params if needed
  };

  return (
    <div className="fixed inset-0 flex items-center justify-center z-50">
      <div
        className="absolute inset-0 bg-black/30 backdrop-blur-sm"
        onClick={handleBackdropClick}
      />
      <div className="relative z-10 w-full max-w-md">{children}</div>
    </div>
  );
}
