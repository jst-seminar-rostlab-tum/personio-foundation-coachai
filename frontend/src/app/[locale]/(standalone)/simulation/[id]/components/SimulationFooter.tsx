'use client';

import { Pause, Play, Phone } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';

export default function SimulationFooter({
  isPaused,
  setIsPaused,
}: {
  isPaused: boolean;
  setIsPaused: (v: boolean) => void;
}) {
  return (
    <div className="flex items-center justify-between md:justify-center md:gap-16 px-6 pt-4 pb-6 bg-white z-10">
      <Button
        size="iconLarge"
        variant="outline"
        onClick={() => setIsPaused(!isPaused)}
        aria-label={isPaused ? 'Resume' : 'Pause'}
      >
        {isPaused ? <Play className="!w-6 !h-6" /> : <Pause className="!w-6 !h-6" />}
      </Button>
      <Link href="/feedback/1">
        <Button size="iconLarge" variant="destructive">
          <Phone className="!w-6 !h-6" />
        </Button>
      </Link>
    </div>
  );
}
