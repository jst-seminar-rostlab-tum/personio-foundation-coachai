'use client';

import { Pause, Play, Phone } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { api } from '@/services/ApiClient';
import { sessionService } from '@/services/SessionService';
import { SessionStatus } from '@/interfaces/Session';
import { SimulationFooterProps } from '@/interfaces/SimulationFooterProps';
import { useRouter } from 'next/navigation';

export default function SimulationFooter({
  isPaused,
  setIsPaused,
  sessionId,
}: SimulationFooterProps) {
  const router = useRouter();

  const handleSessionEnd = async () => {
    try {
      const { data } = await sessionService.updateSession(api, sessionId, {
        status: SessionStatus.COMPLETED,
      });
      router.push(`/feedback/${data.id}`);
    } catch (error) {
      console.error('Error updating session:', error);
    }
  };

  return (
    <div className="flex justify-evenly py-6 z-10">
      <Button
        size="iconLarge"
        variant="outline"
        onClick={() => setIsPaused(!isPaused)}
        aria-label={isPaused ? 'Resume' : 'Pause'}
      >
        {isPaused ? <Play className="!w-6 !h-6" /> : <Pause className="!w-6 !h-6" />}
      </Button>
      <Button onClick={handleSessionEnd} size="iconLarge" variant="destructive">
        <Phone className="!w-6 !h-6" />
      </Button>
    </div>
  );
}
