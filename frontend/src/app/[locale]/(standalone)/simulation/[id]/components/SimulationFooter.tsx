'use client';

import { Phone, Mic, MicOff } from 'lucide-react';
import { Button } from '@/components/ui/Button';

interface SimulationFooterProps {
  isMicActive: boolean;
  toggleMicrophone: () => void;
  isConnected: boolean;
  onDisconnect: () => void;
}

export default function SimulationFooter({
  isMicActive,
  toggleMicrophone,
  isConnected,
  onDisconnect,
}: SimulationFooterProps) {
  return (
    <div className="flex items-center justify-between md:justify-center md:gap-16 px-6 pt-4 pb-6 bg-white z-10">
      <Button size="iconLarge" variant="outline" onClick={toggleMicrophone}>
        {isMicActive ? <Mic className="!w-6 !h-6" /> : <MicOff className="!w-6 !h-6" />}
      </Button>
      <Button
        size="iconLarge"
        variant="destructive"
        onClick={onDisconnect}
        disabled={!isConnected}
        aria-label="Disconnect"
      >
        <Phone className="!w-6 !h-6" />
      </Button>
    </div>
  );
}
