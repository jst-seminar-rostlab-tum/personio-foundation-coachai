'use client';

import { Pause, Play, Phone, Mic, MicOff } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';

export default function SimulationFooter({
  isPaused,
  setIsPaused,
  isMicActive,
  toggleMicrophone,
  isConnected,
  onDisconnect,
}: {
  isPaused: boolean;
  setIsPaused: (v: boolean) => void;
  isMicActive: boolean;
  toggleMicrophone: () => void;
  isConnected: boolean;
  onDisconnect: () => void;
}) {
  return (
    <footer className="flex items-center justify-between md:justify-center md:gap-16 px-6 pt-4 pb-6 bg-white z-10">
      <Button
        size="iconLarge"
        variant="outline"
        onClick={() => setIsPaused(!isPaused)}
        aria-label={isPaused ? 'Resume' : 'Pause'}
      >
        {isPaused ? <Play className="!w-6 !h-6" /> : <Pause className="!w-6 !h-6" />}
      </Button>
      <Button size="iconLarge" variant="outline" onClick={toggleMicrophone}>
        {isMicActive ? <Mic className="!w-6 !h-6" /> : <MicOff className="!w-6 !h-6" />}
      </Button>
      <Link href="/feedback/1">
        <Button
          size="iconLarge"
          variant="destructive"
          onClick={onDisconnect}
          disabled={!isConnected}
          aria-label="Disconnect"
        >
          <Phone className="!w-6 !h-6" />
        </Button>
      </Link>
    </footer>
  );
}
