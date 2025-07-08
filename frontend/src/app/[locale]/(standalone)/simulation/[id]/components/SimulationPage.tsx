'use client';

import { useEffect, useState } from 'react';
import { useWebRTC } from '@/app/[locale]/(standalone)/simulation/[id]/hooks/useWebRTC';
import { showErrorToast } from '@/lib/utils/toast';
import { useTranslations } from 'next-intl';
import { sessionService } from '@/services/SessionService';
import { api } from '@/services/ApiClient';
import { SessionStatus } from '@/interfaces/models/Session';
import { useRouter } from 'next/navigation';
import { Loader2 } from 'lucide-react';
import SimulationHeader from './SimulationHeader';
import SimulationFooter from './SimulationFooter';
import SimulationRealtimeSuggestions from './SimulationRealtimeSuggestions';
import SimulationMessages from './SimulationMessages';

export default function SimulationPageComponent({ sessionId }: { sessionId: string }) {
  const t = useTranslations('Simulation');
  const router = useRouter();
  const [hangupInProgress, setHangupInProgress] = useState(false);

  const {
    isMicActive,
    connectionStatus,
    initWebRTC,
    remoteAudioRef,
    messages,
    elapsedTimeS,
    toggleMic,
    cleanup,
  } = useWebRTC(sessionId);

  useEffect(() => {
    initWebRTC();
    return () => {
      cleanup();
    };
  }, [initWebRTC, sessionId, cleanup]);

  const onDisconnect = async () => {
    try {
      setHangupInProgress(true);
      cleanup();
      const { data } = await sessionService.updateSession(api, sessionId, {
        status: SessionStatus.COMPLETED,
      });
      router.push(`/feedback/${data.id}`);
    } catch (err) {
      setHangupInProgress(false);
      showErrorToast(err, t('sessionEndError'));
    }
  };

  return (
    <div className="flex flex-col h-screen">
      <div className="mb-2">
        <SimulationHeader time={elapsedTimeS} connectionStatus={connectionStatus} />
      </div>

      <div className="flex-1 relative p-4 overflow-y-auto mb-4 md:mb-8 [&::-webkit-scrollbar]:hidden [-ms-overflow-style:'none'] [scrollbar-width:'none']">
        <SimulationMessages messages={messages} />
        {(connectionStatus === 'connecting' ||
          connectionStatus === 'disconnected' ||
          hangupInProgress) && (
          <div className="absolute inset-0 backdrop-blur-sm bg-background z-10"></div>
        )}
      </div>

      <SimulationRealtimeSuggestions />

      <SimulationFooter
        isMicActive={isMicActive}
        toggleMicrophone={toggleMic}
        isConnected={connectionStatus === 'connected'}
        onDisconnect={onDisconnect}
        isDisabled={hangupInProgress}
      />

      {(connectionStatus === 'connecting' ||
        connectionStatus === 'disconnected' ||
        hangupInProgress) && (
        <div className="fixed inset-0 flex flex-col items-center justify-center z-50 pointer-events-none">
          <Loader2 className="h-10 w-10 animate-spin text-marigold-50 mb-4" />
          <div className="text-center text-bw-70 font-medium">
            {hangupInProgress && <p>{t('hangingUp')}</p>}
            {connectionStatus === 'connecting' && <p>{t('connectingMessage')}</p>}
            {connectionStatus === 'disconnected' && !hangupInProgress && (
              <p>{t('disconnectedMessage')}</p>
            )}
          </div>
        </div>
      )}

      <audio ref={remoteAudioRef} autoPlay playsInline />
    </div>
  );
}
