'use client';

import { Phone, Mic, MicOff } from 'lucide-react';
import { Button } from '@/components/ui/Button';

interface SessionFooterProps {
  isMicActive: boolean;
  toggleMicrophone: () => void;
  isConnected: boolean;
  onDisconnect: () => void;
  isDisabled?: boolean;
}

export default function SessionFooter({
  isMicActive,
  toggleMicrophone,
  onDisconnect,
  isDisabled = false,
}: SessionFooterProps) {
  return (
    <div className="flex items-center justify-center gap-16 px-6 pt-4 pb-2 bg-white z-10">
      <Button
        size="iconLarge"
        variant="outline"
        onClick={toggleMicrophone}
        disabled={isDisabled}
        aria-label="Toggle microphone"
      >
        {isMicActive ? <Mic className="!w-6 !h-6" /> : <MicOff className="!w-6 !h-6" />}
      </Button>
      <Button
        size="iconLarge"
        variant="destructive"
        onClick={onDisconnect}
        disabled={isDisabled}
        aria-label="Disconnect"
      >
        <Phone className="!w-6 !h-6" />
      </Button>
    </div>
  );
}
